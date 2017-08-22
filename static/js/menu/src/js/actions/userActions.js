import axios from "axios";

export function fetchUser() {
  return {
    type: "FETCH_USER_FULFILLED",
    payload: {
      name: "Will",
      age: 35,
    }
  }
}

// export const fetchUserNames = () => (dispatch, getState) => {
//   if (!getState().repos.fetching) {
//     dispatch({type: "FETCH_OWNERS"});
//     const ownerArray = getState().repos.map((repo) => {
//       return repo.owner
//     })
//     dispatch({type: "FETCH_OWNERS_FULFILLED", payload: ownerArray})
//     const userArray = ownerArray.map((owner, i) => {
//       axios.get(`/api/v1/user/${owner}`)
//         .then((response) => {
//           dispatch({type: "FETCH_USERNAMES_FULFILLED", username:response.username, index: i})
//         })
//         .catch((err) => {
//           dispatch({type: "FETCH_NAMES_REJECTED", payload: err})
//         })
//     })
//   }
// }



//
// export function setUserName(name) {
//   return {
//     type: 'SET_USER_NAME',
//     payload: name,
//   }
// }
//
// export function setUserAge(age) {
//   return {
//     type: 'SET_USER_AGE',
//     payload: age,
//   }
// }
