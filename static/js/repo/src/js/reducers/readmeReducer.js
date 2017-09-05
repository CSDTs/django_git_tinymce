export default function reducer(state={
    readme: "",
    fetching: false,
    fetched: false,
    error: null,
  }, action) {

    switch (action.type) {
      case "FETCH_README": {

        return {...state, fetching: true}
      }
      case "FETCH_README_REJECTED": {
        return {...state, fetching: false, error: action.payload}
      }
      case "FETCH_README_FULFILLED": {
        return {
          ...state,
          fetching: false,
          fetched: true,
          readme: action.payload,
        }
      }
      
    }

    return state
}
