import React from "react"
import axios from "axios";
import { connect } from "react-redux"

import { fetchRepos } from "../actions/reposActions"
import { fetchTags } from "../actions/tagsActions"


@connect((store) => {
  return {
    repos: store.repos.repos,
    tags: store.tags.tags
  };
})
export default class Layout extends React.Component {
  componentWillMount() {
    //this.props.dispatch(fetchUser())
    this.props.dispatch(fetchRepos())
    this.props.dispatch(fetchTags())
  }

  fetchRepos() {
    this.props.dispatch(fetchRepos())
  }

  fetchUser(num) {
    axios.get(`/api/v1/user/${num}`)
      .then((response) => {
        //dispatch({type: "FETCH_TAGS_FULFILLED", payload: response.data})
        this.owner = response.data.username
        console.log('username', response.data.username)
      })
      .catch((err) => {
        this.owner = "unknown"
      })
    return this.owner
  }

  render() {
    const { user, repos, fetching, fetched, tags } = this.props;

    // if (!repos.length) {
    //   return <button onClick={this.fetchRepos.bind(this)}>load repos</button>
    // }

    //const mappedTweets = tweets.map(tweet => <li key={tweet.id}>{tweet.text}</li>)

    const mappedRepos = this.props.repos.map(repo => {
      return  <a href={`/${repo.owner_username}/${repo.name}`.toLowerCase()} key={repo.id}><div className="col-md-4" ><img src="https://dummyimage.com/400x300/000/fff" width="100%" className="img-responsive"/>{repo.name} by { repo.owner_username }</div></a>
    })

    const mappedTags = this.props.tags.map(tag => {
      function toTitleCase(str)
      {
          return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
      }
      let titled = toTitleCase(tag.title)
      console.log('titled', titled)
      return <li key={tag.id}><a href="#" >{titled}</a></li>
    })

    return <div>
      <div className="row">
        <div className="col-md-12">
          <h1 className="text-center">Repositories</h1>
        </div>
      </div>
      <div className="row">
        <div className="col-md-2">
          <ul style={{listStyle: 'none', fontSize: '.90em'}}>
            Tags
            {mappedTags}
          </ul>
        </div>
        <div className="col-md-10">
          <div className="row">
            {mappedRepos}
          </div>

        </div>
      </div>

    </div>
  }
}
