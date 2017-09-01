import axios from "axios";

export function fetchFiles() {
  return function(dispatch) {
    dispatch({type: "FETCH_FILES"});


    axios.get(`/api/v1/files/${window.props.repo_id}/${window.props.directory}`)
      .then((response) => {
        console.log('data.files', response.data)
        // if response.data.files == undefined {
        //   response.data.files = []
        // }
        dispatch({type: "FETCH_FILES_FULFILLED", payload: response.data.files})
        dispatch({type: "FETCH_IS_AUTHOR_FULFILLED", payload: response.data.is_owner})
        dispatch({type: "FETCH_BRANCHES_FULFILLED", payload: response.data.branches})
        dispatch({type: "FETCH_MESSAGE_FULFILLED", payload: response.data.message})
        dispatch({type: "FETCH_COMMITTER_FULFILLED", payload: response.data.committer})
        dispatch({type: "FETCH_HEX_FULFILLED", payload: response.data.hex})
        dispatch({type: "FETCH_TIME_FULFILLED", payload: response.data.time})

      })
      .catch((err) => {
        dispatch({type: "FETCH_FILES_REJECTED", payload: err})
      })
  }
}
