#include <stdbool.h>
#include <stdio.h>
#include <Python.h>

const unsigned char FILL_TYPES[] = {0x00, 0xFF};
const int MAX_ITERS = 64;
const int GET_LIST = 0;
const int GET_COUNT = 1;
const int IS_EXIST = 2;


typedef struct CompressedSeqIter {
    size_t pos;
    size_t remaining_bytes;
    size_t len;
    unsigned char* buffer;
    unsigned char fill_type;
    bool is_noise;
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

bool _check_request(int request) {
    if (request != GET_LIST && request != GET_COUNT && request != IS_EXIST) {
        PyErr_SetString(PyExc_ValueError, "Selected mode should be GET_LIST=0, GET_COUNT=1, IS_EXIST=2");
        return false;
    }
    return true;
}

PyObject* _calc_bit_index_result(int request,
                                 CompressedSeqIter* seq_iters,
                                 size_t iters_num,
                                 unsigned int alloc_size) {
    unsigned int *result_list_native = NULL;
    if (request == GET_LIST) {
        result_list_native = malloc(sizeof(unsigned int) * alloc_size);
        if (NULL == result_list_native) {
            PyErr_SetString(PyExc_MemoryError, "Cannot allocate result list");
            return NULL;
        }
    }
    int iter_results[MAX_ITERS]; 
    bool value_exists = false;
    int byte_index = 0;
    size_t result_index = 0;
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
                    if (IS_EXIST == request) {
                        value_exists = true;
                        goto end_of_loop;
                    }
                    if (result_index == alloc_size) {
                        free(result_list_native);
                        PyErr_SetString(PyExc_MemoryError, "The number of results greater than allocated size");
                        return NULL;
                    }
                    if (request == GET_LIST) {
                        result_list_native[result_index] = output_val;
                    }
                    result_index++;
                }
            }
        }
        byte_index++;
    }

    end_of_loop:

    switch (request)
    {
    case IS_EXIST:
        if (value_exists) Py_RETURN_TRUE;
        Py_RETURN_FALSE;
    case GET_COUNT:
        return PyLong_FromLong(result_index);
    case GET_LIST:
        PyObject* result_list = PyList_New(result_index);
        if (NULL == result_list) {
            free(result_list_native);
            PyErr_SetString(PyExc_MemoryError, "Cannot create result list");
            return NULL;
        }
        for (size_t i = 0; i < result_index; i++) {
            PyObject* py_long = PyLong_FromLong(result_list_native[i]);
            if (NULL == py_long) {
                free(result_list_native);
                PyErr_SetString(PyExc_MemoryError, "Cannot create result list element");
                Py_CLEAR(result_list);
            }
            int set_res = PyList_SetItem(result_list, i, py_long);
            if (set_res < 0) {
                free(result_list_native);
                Py_CLEAR(result_list);
                return NULL;
            }
        }
        free(result_list_native);

        return result_list;
    default:
        PyErr_SetString(PyExc_ValueError, "Impossible state. Selected mode should be GET_LIST=0, GET_COUNT=1, IS_EXIST=2");
    }
    return NULL;
}

static PyObject* bit_index_native(PyObject* self, PyObject* args) {
    PyObject* compressed_seq;
    unsigned int alloc_size;
    int request;

    if (!PyArg_ParseTuple(args, "OIi", &compressed_seq, &alloc_size, &request)) {
        return NULL;
    }

    if (!_check_request(request)) {
        return NULL;
    }


    Py_buffer buffer;
    if (PyObject_GetBuffer(compressed_seq, &buffer, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    CompressedSeqIter seq_iter;
    CompressedSeqIter_new(&seq_iter, &buffer);

    PyBuffer_Release(&buffer);

    return _calc_bit_index_result(
        request,
        &seq_iter,
        1,
        alloc_size
    );
}


static PyObject* bit_and_op_index_native(PyObject* self, PyObject* args) {

    PyObject* iterable_of_buffers;
    unsigned int alloc_size;
    int request;
    
    if (!PyArg_ParseTuple(args, "OIi", &iterable_of_buffers, &alloc_size, &request)) {
        return NULL;
    }

    if (!_check_request(request)) {
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
            Py_DECREF(next);
            Py_DECREF(iter);
            return NULL;
        }
        if (iters_num == MAX_ITERS) {
            PyBuffer_Release(&buffer);
            Py_DECREF(next);
            Py_DECREF(iter);
            PyErr_SetString(PyExc_BufferError, "Too many buffers to process");
            return NULL;
        }
        CompressedSeqIter_new(&seq_iters[iters_num], &buffer);
        iters_num++;

        PyBuffer_Release(&buffer);
        Py_DECREF(next);
    }
    Py_DECREF(iter);

    if (iters_num < 2) {
        PyErr_SetString(PyExc_BufferError, "Too few buffers to process, should be at least 2");
        return NULL;
    }

    return _calc_bit_index_result(
        request,
        seq_iters,
        iters_num,
        alloc_size
    );
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