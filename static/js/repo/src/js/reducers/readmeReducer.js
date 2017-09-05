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
      // case "ADD_TWEET": {
      //   return {
      //     ...state,
      //     repos: [...state.repos, action.payload],
      //   }
      // }
      // case "UPDATE_TWEET": {
      //   const { id, text } = action.payload
      //   const newTweets = [...state.repos]
      //   const tweetToUpdate = newTweets.findIndex(tweet => tweet.id === id)
      //   newTweets[tweetToUpdate] = action.payload;
      //
      //   return {
      //     ...state,
      //     repos: newTweets,
      //   }
      // }
      // case "DELETE_TWEET": {
      //   return {
      //     ...state,
      //     repos: state.repos.filter(tweet => tweet.id !== action.payload),
      //   }
      // }
    }

    return state
}
