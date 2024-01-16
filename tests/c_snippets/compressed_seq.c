#include <stdbool.h>
#include <stdio.h>
#include <Python.h>

const unsigned char FILL_TYPES[] = {0x00, 0xFF};
const int MAX_ITERS = 64;

typedef struct CompressedSeqIter {
    size_t pos;
    size_t remaining_bytes;
    bool is_noise;
    unsigned char fill_type;
    size_t len;
    unsigned char* buffer;
    bool stop_iteration;
} CompressedSeqIter;


void CompressedSeqIter_read_control_byte(CompressedSeqIter* seq_iter) {
    if (seq_iter->pos >= (size_t) seq_iter->len) {
        seq_iter->stop_iteration = true;
    }
    unsigned char* buffer = seq_iter->buffer;
    unsigned char byte = buffer[seq_iter->pos];
    seq_iter->is_noise = byte >> 7;
    bool is_long;
    size_t bytes_count;
    if (seq_iter->is_noise) {
        bytes_count = byte & 0x3f;
        is_long = (byte >> 6) & 1;
        if (is_long) {
            seq_iter->pos++;
            bytes_count = (bytes_count << 8) | buffer[seq_iter->pos];
        }
    } else {
        seq_iter->fill_type = FILL_TYPES[byte >> 6];
        bytes_count = byte & 0x1F;
        is_long = (byte >> 5) & 1;
        if (is_long) {
            seq_iter->pos++;
            bytes_count = (bytes_count << 8) | buffer[seq_iter->pos];
        }
    }
    ++seq_iter->pos;
    seq_iter->remaining_bytes = bytes_count;
}

void CompressedSeqIter_new(CompressedSeqIter* seq_iter, Py_buffer* buf) {
    seq_iter->pos = 0;
    seq_iter->stop_iteration = false;
    seq_iter->len = buf->len;
    seq_iter->buffer = buf->buf;
    CompressedSeqIter_read_control_byte(seq_iter);
};

void CompressedSeqIter_seek(CompressedSeqIter* seq_iter, size_t bytes_to_seek) {
    while (seq_iter->remaining_bytes < bytes_to_seek) {
        bytes_to_seek -= seq_iter->remaining_bytes;
        if (seq_iter->is_noise) {
            seq_iter->pos += seq_iter->remaining_bytes;
        }
        CompressedSeqIter_read_control_byte(seq_iter);
    }
    seq_iter->remaining_bytes -= bytes_to_seek;
    if (seq_iter->is_noise) {
        seq_iter->pos += bytes_to_seek;
    }
    if (seq_iter->remaining_bytes == 0) {
        CompressedSeqIter_read_control_byte(seq_iter);
    }
}

int CompressedSeqIter_next(CompressedSeqIter* seq_iter) {
    if (seq_iter->stop_iteration) {
        return -1;
    }
    unsigned char ret_val;
    if (seq_iter->is_noise) {
        unsigned char* buffer = seq_iter->buffer;
        ret_val = buffer[seq_iter->pos];
    } else {
        ret_val = seq_iter->fill_type;
    }
    CompressedSeqIter_seek(seq_iter, 1);
    return ret_val;
}

size_t CompressedSeqIter_seekable_bytes(CompressedSeqIter* seq_iter) {
    if (seq_iter->is_noise || seq_iter->fill_type == 0xFF) {
        return 0;
    }
    return seq_iter->remaining_bytes;
}


static PyObject* bit_index_native(PyObject* self, PyObject* args) {
    PyObject* compressed_seq;

    if (!PyArg_ParseTuple(args, "O", &compressed_seq)) {
        return NULL;
    }


    Py_buffer buffer;
    if (PyObject_GetBuffer(compressed_seq, &buffer, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    CompressedSeqIter seq_iter;
    CompressedSeqIter_new(&seq_iter, &buffer);

    PyBuffer_Release(&buffer);

    PyObject* result_list = PyList_New(0);
    if (NULL == result_list) {
        PyErr_SetString(PyExc_MemoryError, "Cannot allocate result list");
        return NULL;
    }

    for(int byte_index = 0, decompressed_val_i;
        (decompressed_val_i = CompressedSeqIter_next(&seq_iter)) >= 0;) {
        unsigned char decompressed_val = (unsigned char) decompressed_val_i;
        if (decompressed_val == 0) {
            size_t seekable_bytes = CompressedSeqIter_seekable_bytes(&seq_iter);
            if (seekable_bytes > 0) {
                byte_index += seekable_bytes;
                CompressedSeqIter_seek(&seq_iter, seekable_bytes);
            }
        } else {
            for (int bit_num = 7; bit_num >= 0; bit_num--) {
                if ((decompressed_val >> bit_num) & 1) {
                    unsigned int output_val = byte_index * 8 + (7 - bit_num);
                    PyObject* py_long = PyLong_FromLong(output_val);
                    if (NULL == py_long) {
                        goto release_list;
                    }
                    int res_append = PyList_Append(result_list, py_long);
                    Py_DECREF(py_long);
                    if (res_append < 0) {
                        goto release_list;
                    }
                }
            }
        }
        byte_index++;
    }

    if (false) {
        release_list:
            PyErr_SetString(PyExc_MemoryError, "Cannot create result list");
            Py_CLEAR(result_list); // result_list will also be NULL after clear
    }

    return result_list;
}


static PyObject* bit_and_op_index_native(PyObject* self, PyObject* args) {

    PyObject* iterable_of_buffers;
    
    if (!PyArg_ParseTuple(args, "O", &iterable_of_buffers)) {
        return NULL;
    }

    if (!PySequence_Check(iterable_of_buffers)) {
        PyErr_SetString(PyExc_TypeError, "bit_and_op_index_native expects a sequence");
        return NULL;
    }

    size_t iters_num = 0;
    CompressedSeqIter seq_iters[MAX_ITERS];
    int iter_results[MAX_ITERS];

    PyObject *iter = PyObject_GetIter(iterable_of_buffers);
    if (NULL == iter) {
        return NULL;
    }

    for (PyObject *next; (next = PyIter_Next(iter)) != NULL;) {

        Py_buffer buffer;
        if (PyObject_GetBuffer(next, &buffer, PyBUF_SIMPLE) < 0) {
            return NULL;
        }
        if (iters_num == MAX_ITERS) {
            PyBuffer_Release(&buffer);
            
            PyErr_SetString(PyExc_BufferError, "Too many buffers to process");
            return NULL;
        }
        CompressedSeqIter_new(&seq_iters[iters_num], &buffer);
        iters_num++;

        PyBuffer_Release(&buffer);
    }

    if (iters_num < 2) {
        PyErr_SetString(PyExc_BufferError, "Too few buffers to process, should be at least 2");
        return NULL;
    }

    PyObject* result_list = PyList_New(0);
    int byte_index = 0;
    while(1) {
        for (size_t i = 0; i < iters_num; i++) {
            iter_results[i] = CompressedSeqIter_next(&seq_iters[i]);
        }
        if (iter_results[0] < 0) {
            break;
        }
        unsigned char byte = (unsigned char)iter_results[0];
        unsigned char all_merged_bytes = (unsigned char)iter_results[0];
        for (size_t i = 1; i < iters_num; i++) {
            byte &= iter_results[i];
            all_merged_bytes |= iter_results[i];
        }
        if (all_merged_bytes == 0) {
            int max_seekable_bytes = -1;
            for (size_t i = 0; i < iters_num; i++) {
                int seekable_bytes = (int)CompressedSeqIter_seekable_bytes(&seq_iters[i]);
                if (seekable_bytes > max_seekable_bytes) {
                    max_seekable_bytes = seekable_bytes;
                }
            }
            if (max_seekable_bytes > 0) {
                byte_index += max_seekable_bytes;
                for (size_t i = 0; i < iters_num; i++) {
                    CompressedSeqIter_seek(&seq_iters[i], (size_t) max_seekable_bytes);
                }
            }
        }
        if (byte != 0) {
            for (int bit_num = 7; bit_num >= 0; bit_num--) {
                if ((byte >> bit_num) & 1) {
                    unsigned int output_val = byte_index * 8 + (7 - bit_num);
                    PyObject* py_long = PyLong_FromLong(output_val);
                    if (NULL == py_long) {
                        goto release_list;
                    }
                    int res_append = PyList_Append(result_list, py_long);
                    Py_DECREF(py_long);
                    if (res_append < 0) {
                        goto release_list;
                    }
                }
            }
        }
        byte_index++;
    }

    if (false) {
        release_list:
            PyErr_SetString(PyExc_MemoryError, "Cannot create result list");
            Py_CLEAR(result_list);
    }

    return result_list;
}

static PyMethodDef methods[] = {
    {"bit_index_native", bit_index_native, METH_VARARGS, "Bit index"},
    {"bit_and_op_index_native", bit_and_op_index_native, METH_VARARGS, "Bit indexes with operator"},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef compressed_seq = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "compressed_seq",
    .m_doc = "compressed_seq",
    .m_methods = methods
};

PyMODINIT_FUNC PyInit_compressed_seq() {
    // printf("This is a test!\n");
    return PyModule_Create(&compressed_seq);
}