#include <stdio.h>
#include <Python.h>


static PyObject* test_bytearray001(PyObject* self, PyObject* args) {
    PyObject* bytearray_obj;
    Py_buffer buffer;

    if (!PyArg_ParseTuple(args, "O", &bytearray_obj)) {
        return NULL;
    }

    if (PyObject_GetBuffer(bytearray_obj, &buffer, PyBUF_SIMPLE) < 0) {
        return NULL;
    }


    char* buf = buffer.buf;
    printf("buffer length: %ld\n", buffer.len);
    for(Py_ssize_t i = 0; i < buffer.len; i++) {
        printf("%x", buf[i] & 0xff);
    }
    printf("\n");

    PyBuffer_Release(&buffer);
    

    Py_RETURN_NONE;
}

static PyObject* test_iterable_of_buffers(PyObject* self, PyObject* args) {
    PyObject* iterable_of_buffers;
    
    if (!PyArg_ParseTuple(args, "O", &iterable_of_buffers)) {
        return NULL;
    }

    if (!PySequence_Check(iterable_of_buffers)) {
        PyErr_SetString(PyExc_TypeError, "test_iterable_of_buffers expects a sequence");
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
    {"test_bytearray001", test_bytearray001, METH_VARARGS, "Get the content of a bytearray as bytes"},
    {"test_iterable_of_buffers", test_iterable_of_buffers, METH_VARARGS, "Print content of iterables of buffers"},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef test_bytearray001_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "test_bytearray001",
    .m_doc = "test_bytearray001",
    .m_methods = methods
};

PyMODINIT_FUNC PyInit_test_bytearray001() {
    printf("This is a test!\n");
    return PyModule_Create(&test_bytearray001_module);
}