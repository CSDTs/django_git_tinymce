import axios from "axios";

export function fetchRepos() {
  return function(dispatch) {
    dispatch({type: "FETCH_REPOS"});


    axios.get("/api/v1/repository")
      .then((response) => {
        dispatch({type: "FETCH_REPOS_FULFILLED", payload: response.data})
      })
      .catch((err) => {
        dispatch({type: "FETCH_REPOS_REJECTED", payload: err})
      })
  }
}

// export function filterRepos(response) {
//   return function(dispatch) {
//     console.log('response', response)
//     dispatch({type: "FILTER_REPOS", payload: response});
//
//
//
//   }
// }


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
