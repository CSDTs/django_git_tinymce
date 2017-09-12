export default function reducer(state={
    repos: [],
    copy: [],
    fetching: false,
    fetched: false,
    error: null,
  }, action) {

    switch (action.type) {
      case "FETCH_REPOS": {
        return {...state, fetching: true}
      }
      case "FETCH_REPOS_REJECTED": {
        return {...state, fetching: false, error: action.payload}
      }
      case "FETCH_REPOS_FULFILLED": {
        return {
          ...state,
          fetching: false,
          fetched: true,
          repos: action.payload,
          copy: action.payload,
        }
      }
      case "FILTER_REPOS": {
        return {...state, copy: action.payload}
      }

    }

    return state
}
