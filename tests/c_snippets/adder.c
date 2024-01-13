#include <stdio.h>
#include <Python.h>

PyObject *add(PyObject *self, PyObject *args) {
    int x, y;
    PyArg_ParseTuple(args, "ii", &x, &y);
    return PyLong_FromLong((long)(x + y));
}

static PyMethodDef methods[] = {
    {"add", add, METH_VARARGS, "Adds two numbers together" },
    {NULL, NULL, 0, NULL}
};

static PyModuleDef adder = {
    PyModuleDef_HEAD_INIT,
    "adder",
    "This module is used to work with compressed data",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_adder() {
    printf("This is a test!\n");
    return PyModule_Create(&adder);
}
