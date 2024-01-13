#include <stdio.h>
#include <Python.h>

static PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",
    "This module is used to work with compressed data",
    -1
};

PyMODINIT_FUNC PyInit_adder() {
    PyObject *m;

    m = PyModule_Create(&spammodule);
    if (m == NULL)
        return NULL;

    PyObject* SpamError = PyErr_NewException("spam.error", NULL, NULL);
    Py_XINCREF(SpamError);
    if (PyModule_AddObject(m, "error", SpamError) < 0) {
        Py_XDECREF(SpamError);
        Py_CLEAR(SpamError);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
