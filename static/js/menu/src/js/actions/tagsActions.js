import axios from "axios";

export function fetchTags() {
  return function(dispatch) {
    dispatch({type: "FETCH_TAGS"});


    axios.get("/api/v1/tag")
      .then((response) => {
        dispatch({type: "FETCH_TAGS_FULFILLED", payload: response.data})
      })
      .catch((err) => {
        dispatch({type: "FETCH_TAGS_REJECTED", payload: err})
      })
  }
}
