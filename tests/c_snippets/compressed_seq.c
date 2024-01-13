#include <stdbool.h>
#include <stdio.h>
#include <Python.h>

const unsigned char FILL_TYPES[] = {0x00, 0xFF};

typedef struct CompressedSeqIter {
    size_t pos;
    size_t remaining_bytes;
    bool is_noise;
    unsigned char fill_type;
    const Py_buffer* buf;
    bool stop_iteration;
} CompressedSeqIter;


void CompressedSeqIter_read_control_byte(CompressedSeqIter* seq_iter) {
    if (seq_iter->pos > (size_t) seq_iter->buf->len) {
        seq_iter->stop_iteration = true;
    }
    unsigned char* buffer = seq_iter->buf->buf;
    unsigned char byte = buffer[seq_iter->pos];
    seq_iter->is_noise = byte >> 7;
    // printf("Control byte: %x\n", byte & 0xff);
    bool is_long;
    size_t bytes_count;
    if (seq_iter->is_noise) {
        // printf("Is noise\n");
        bytes_count = byte & 0x3f;
        is_long = (byte >> 6) & 1;
        // printf("is_long %d\n", is_long);
        if (is_long) {
            bytes_count = (bytes_count << 8) | buffer[++seq_iter->pos];
        }
    } else {
        // printf("Fill byte\n");
        seq_iter->fill_type = FILL_TYPES[byte >> 6];
        bytes_count = byte & 0x1F;
        is_long = (byte >> 5) & 1;
        if (is_long) {
            bytes_count = (bytes_count << 8) | buffer[++seq_iter->pos];
        }
    }
    ++seq_iter->pos;
    seq_iter->remaining_bytes = bytes_count;
}

void CompressedSeqIter_new(CompressedSeqIter* seq_iter, const Py_buffer* buf) {
    seq_iter->pos = 0;
    seq_iter->stop_iteration = false;
    seq_iter->buf = buf;
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
        unsigned char* buffer = seq_iter->buf->buf;
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

    // printf("This is stub function!\n");

    Py_buffer buffer;
    if (PyObject_GetBuffer(compressed_seq, &buffer, PyBUF_SIMPLE) < 0) {
        return NULL;
    }

    CompressedSeqIter seq_iter;
    CompressedSeqIter_new(&seq_iter, &buffer);

    PyObject* result_list = PyList_New(0);

    // int total_bytes = 0;
    int byte_index = 0;
    int decompressed_val_i;
    while((decompressed_val_i = CompressedSeqIter_next(&seq_iter)) >= 0) {
        // decompressed_val_i = CompressedSeqIter_next(&seq_iter);
        // printf("Decompressed val i %d\n", decompressed_val_i);
        // if (decompressed_val_i < 0) {
        //     break;
        // }
        unsigned char decompressed_val = (unsigned char) decompressed_val_i;
        // printf("decompressed val: %x => \n", decompressed_val & 0xFF);
        if (decompressed_val == 0) {
            size_t seekable_bytes = CompressedSeqIter_seekable_bytes(&seq_iter);
            // printf("Seekable bytes: %d\n", (int)seekable_bytes);
            if (seekable_bytes > 0) {
                byte_index += seekable_bytes;
                CompressedSeqIter_seek(&seq_iter, seekable_bytes);
            }
        } else {
            for (int bit_num = 7; bit_num >= 0; bit_num--) {
                // printf("Bit num %d\n", bit_num);
                if ((decompressed_val >> bit_num) & 1) {
                    unsigned int output_val = byte_index * 8 + (7 - bit_num);
                    // printf("output val: %d\n", output_val);
                    PyList_Append(result_list, PyLong_FromLong(output_val));
                }
            }
        }
        byte_index++;
        // total_bytes++;
    }
    // printf("Total bytes: %d\n", total_bytes);
    

    // char* buf = buffer.buf;
    // printf("buffer length: %ld\n", buffer.len);
    // for(Py_ssize_t i = 0; i < buffer.len; i++) {
    //     printf("%x", buf[i] & 0xff);
    // }
    // printf("\n");

    PyBuffer_Release(&buffer);

    // Py_RETURN_NONE;
    return result_list;
}

static PyObject* bit_op_index_native(PyObject* self, PyObject* args) {
    PyObject* iterable_of_buffers;
    
    if (!PyArg_ParseTuple(args, "O", &iterable_of_buffers)) {
        return NULL;
    }

    if (!PySequence_Check(iterable_of_buffers)) {
        PyErr_SetString(PyExc_TypeError, "bit_op_index_native expects a sequence");
        return NULL;
    }

    PyObject *iter = PyObject_GetIter(iterable_of_buffers);
    if (!iter) {
        return NULL;
    }

    while (1) {

        PyObject *next = PyIter_Next(iter);
        if (!next) {
            break;
        }

        PyTypeObject* type = next->ob_type;
        printf("Type of inner: %s\n", type->tp_name);
        
        Py_buffer buffer;
        if (PyObject_GetBuffer(next, &buffer, PyBUF_SIMPLE) < 0) {
            return NULL;
        }

        char* buf = buffer.buf;
        printf("buffer length: %ld\n", buffer.len);
        for(Py_ssize_t i = 0; i < buffer.len; i++) {
            printf("%x", buf[i] & 0xff);
        }
        printf("\n");

        PyBuffer_Release(&buffer);
    }

    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"bit_index_native", bit_index_native, METH_VARARGS, "Bit index"},
    {"bit_op_index_native", bit_op_index_native, METH_VARARGS, "Bit indexes with operator"},
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