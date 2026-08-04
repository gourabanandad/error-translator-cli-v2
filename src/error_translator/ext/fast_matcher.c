// Include the primary Python C API header.
#include <Python.h>
// Use Py_ssize_t for lengths and sizes to ensure 64-bit cleanliness.
#define PY_SSIZE_T_CLEAN

/*
 * match_error_loop:
 * Iterates through a list of regex compiled rules and attempts to match
 * a provided error line.
 * 
 * Arguments (expected from Python):
 *  - error_line (str): The specific line from the traceback/error log.
 *  - rules_list (list): A list of tuples, where each tuple contains
 *                       (compiled_pattern, rule_dict).
 *
 * Returns:
 *  - A tuple (match_object, rule_dict) if a match is found.
 *  - Py_None if no match is found.
 *  - NULL on errors.
 */
static PyObject* match_error_loop(PyObject* self, PyObject* args){
  PyObject *error_line;
  PyObject *rules_list;

  // Parse the incoming arguments: "U" for Unicode string, "O" for any Python object.
  if (!PyArg_ParseTuple(args, "UO", &error_line, &rules_list)) {
    return NULL;
  }
  
  // Validate that the second argument is indeed a list.
  if(!PyList_Check(rules_list)) {
    PyErr_SetString(PyExc_TypeError, "rules_list must be a list");
    return NULL;
  }

  // Get the size of the rules_list to iterate over.
  Py_ssize_t list_size = PyList_Size(rules_list);

  // Iterate over each (pattern, rule_dict) tuple.
  for(Py_ssize_t i = 0; i < list_size; i++) {
    // Note: PyList_GetItem and PyTuple_GetItem return borrowed references.
    PyObject *tuple = PyList_GetItem(rules_list, i);
    PyObject *pattern = PyTuple_GetItem(tuple, 0);
    PyObject *rule_dict = PyTuple_GetItem(tuple, 1);

    // Call the "search" method on the compiled pattern object, passing the error_line.
    PyObject *match = PyObject_CallMethod(pattern, "search", "O", error_line);
    
    // If the method call failed or raised an exception, continue to the next iteration.
    if(match == NULL) {
      // A regex raised an exception (e.g. bad pattern). Clear it so it
      // doesn't leak into the next iteration's PyObject_CallMethod call.
      PyErr_Clear();
      continue;
    }

    // Check if the search returned a valid match object (not Py_None).
    if(match != Py_None) {
      // Pack the match object and rule_dict into a new tuple (a new reference).
      PyObject *result = PyTuple_Pack(2, match, rule_dict);
      Py_DECREF(match); // Release our reference to the match object.
      return result;    // Return the (match, rule_dict) tuple to Python.
    }

    // If it was Py_None, just decrease the reference count and continue.
    Py_DECREF(match);
  }

  // If no patterns matched, return Python's None object.
  Py_RETURN_NONE;
}

/* 
 * Array mapping Python method names to our C functions.
 */
static PyMethodDef FastMatcherMethods[] = {
  {"match_loop", match_error_loop, METH_VARARGS, "Iterate through regex rules quickly."},
  {NULL, NULL, 0, NULL} // Sentinel value indicating the end of the methods array.
};

/* 
 * Structure that defines the module.
 */
static struct PyModuleDef fastmatchermodule = {
  PyModuleDef_HEAD_INIT,
  "fast_matcher",                              // m_name
  "C Extension for fast regex rule matching.", // m_doc
  -1,                                          // m_size (state kept in global variables)
  FastMatcherMethods                           // m_methods
};

/*
 * Module initialization function, called when Python imports the module.
 */
PyMODINIT_FUNC PyInit_fast_matcher(void){
  return PyModule_Create(&fastmatchermodule);
}