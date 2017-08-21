import React from "react"
import { connect } from "react-redux"

import { fetchUser } from "../actions/userActions"
import { fetchRepos } from "../actions/reposActions"
import { fetchTags } from "../actions/tagsActions"


@connect((store) => {
  return {
    user: store.user.user,
    userFetched: store.user.fetched,
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

  render() {
    const { user, repos, fetching, fetched, tags } = this.props;

    // if (!repos.length) {
    //   return <button onClick={this.fetchRepos.bind(this)}>load repos</button>
    // }

    //const mappedTweets = tweets.map(tweet => <li key={tweet.id}>{tweet.text}</li>)
    const mappedRepos = this.props.repos.map(repo =>
      /* need to find method of pinging owner ids to match to username for url */
      <a href="#" key={repo.id}><div className="col-md-4" ><img src="https://dummyimage.com/400x300/000/fff" width="100%" className="img-responsive"/>{repo.name} - by { repo.owner }</div></a>
    )
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
          <h1 className="text-center">OPENS</h1>
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
