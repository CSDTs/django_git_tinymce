import axios from "axios";

export function fetchRepo() {
  return function(dispatch) {
    dispatch({type: "FETCH_REPO"});


    axios.get(`/api/v1/repository/${window.props.repo_id}`)
      .then((response) => {
        dispatch({type: "FETCH_REPO_FULFILLED", payload: response.data})
      })
      .catch((err) => {
        dispatch({type: "FETCH_REPO_REJECTED", payload: err})
      })
  }
}


//
// export function addTweet(id, text) {
//   return {
//     type: 'ADD_TWEET',
//     payload: {
//       id,
//       text,
//     },
//   }
// }
//
// export function updateTweet(id, text) {
//   return {
//     type: 'UPDATE_TWEET',
//     payload: {
//       id,
//       text,
//     },
//   }
// }
//
// export function deleteTweet(id) {
//   return { type: 'DELETE_TWEET', payload: id}
// }
