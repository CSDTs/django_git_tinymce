export default function reducer(state={
    files: {},
    fetching: false,
    fetched: false,
    error: null,
    is_owner: null,
    is_editor: null,
    message: null,
    committer: null,
    hex: null,
    time: null,
  }, action) {

    switch (action.type) {
      case "FETCH_FILES": {

        return {...state, fetching: true}
      }
      case "FETCH_FILES_REJECTED": {
        return {...state, fetching: false, error: action.payload}
      }
      case "FETCH_FILES_FULFILLED": {
        return {
          ...state,
          fetching: false,
          fetched: true,
          files: action.payload,
        }
      }
      case "FETCH_IS_AUTHOR_FULFILLED": {
        return {
          ...state,
          is_owner: action.payload
        }
      }
      case "FETCH_BRANCHES_FULFILLED": {
        return {
          ...state,
          branches: action.payload
        }
      }
      case "FETCH_MESSAGE_FULFILLED": {
        return {
          ...state,
          message: action.payload
        }
      }
      case "FETCH_COMMITTER_FULFILLED": {
        return {
          ...state,
          committer: action.payload
        }
      }
      case "FETCH_HEX_FULFILLED": {
        return {
          ...state,
          hex: action.payload
        }
      }
      case "FETCH_EDITORS_FULFILLED": {
        return {
          ...state,
          is_editor: action.payload
        }
      }
      case "FETCH_TIME_FULFILLED": {
        if (action.payload == null) {
          return {
            ...state,
            time: "\"2017-42-42T26:00:00\""
          }
        } else {
          return {
            ...state,
            time: action.payload
          }
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
