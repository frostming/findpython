use pyo3::prelude::*;

use super::Provider;

pub struct PyObjectProvider {
    inner: PyObject,
}

impl PyObjectProvider {
    pub fn new(obj: PyObject) -> Self {
        Self { inner: obj }
    }
}

impl Provider for PyObjectProvider {
    fn create() -> Option<Self>
    where
        Self: Sized,
    {
        None
    }

    fn find_pythons(&self) -> Vec<crate::python::PythonVersion> {
        let result: PyResult<Vec<crate::python::PythonVersion>> = Python::with_gil(|py| {
            let result = self.inner.call_method0(py, "find_pythons")?;
            result.extract(py)
        });
        result.unwrap()
    }
}
