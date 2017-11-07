import axios from "axios";

export function fetchReadme() {
  return function(dispatch) {
    dispatch({type: "FETCH_FILES"});


    axios.get(`/${window.props.repo_owner}/${window.props.repo_name}/blob${(window.props.directory !== '') ? `/${window.props.directory}` : ``}/README.html`)
      .then((response) => {
        console.log('data.files', response.data)
        // if response.data.files == undefined {
        //   response.data.files = []
        // }
        dispatch({type: "FETCH_README_FULFILLED", payload: response.data})

      })
      .catch((err) => {
        dispatch({type: "FETCH_README_REJECTED", payload: err})
      })
  }
}
