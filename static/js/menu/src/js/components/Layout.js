import React from "react"
import axios from "axios";
import { connect } from "react-redux"
import { Table, Pagination } from 'react-bootstrap'
import { push } from 'react-router-redux'

import { fetchRepos } from "../actions/reposActions"
import { fetchTags } from "../actions/tagsActions"
import { routerActions } from 'react-router-redux';
import queryString from 'query-string'
import { withRouter } from 'react-router'








@connect((store) => {

  return {
    repos: store.repos.repos,
    tags: store.tags.tags,
    page: 1,
    copy: store.repos.copy,
    //page: Number(store.routing.locationBeforeTransitions.query.page) || 1
  };
})



export default class Layout extends React.Component {




  constructor(props) {
    super(props);
    this.changePage = this.changePage.bind(this);
    this.state = {boolean: false};
  }

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

  loadTags(id) {

    const reduce = this.props.tags.filter((tag) => {
      return tag.id == id
    })
    let array1 = []
    const repos_filtered = this.props.repos.filter((repo) => {
      const okay = reduce.map(tag_repo => {
        const okay3 = tag_repo.repos.filter((tag) => {
          console.log('tag', tag)
          console.log(repo.id, 'repo.id')
          return tag == repo.id
        })
        console.log('okay3', okay3)
        return okay3
      })
      console.log(okay, 'okay')
      console.log(repo, 'repo')
      if (okay[0].length == 0) {
        return false
      }
      else {
        return true
      }
    })
    console.log('repos_filtered', repos_filtered)

    this.props.dispatch({type: "FILTER_REPOS", payload: repos_filtered})

  }

  none() {
    this.props.dispatch({type: "FILTER_REPOS", payload: this.props.repos})
  }



  render() {
    let boolean = this.state.boolean
    console.log('boolean', boolean)

    function getParameterByName(name, url) {
        if (!url) url = window.location.href;
        name = name.replace(/[\[\]]/g, "\\$&");
        var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
        if (!results) return null;
        if (!results[2]) return '';
        return decodeURIComponent(results[2].replace(/\+/g, " "));
    }
    let query = getParameterByName('page') || 1
    console.log(query, 'query')
    const { user, repos, fetching, fetched, tags } = this.props;
    const per_page = 20;
    const pages = Math.ceil(this.props.copy.length / per_page );
    const current_page = query
    console.log('current_page', current_page)
    const start_offset = (current_page - 1) * per_page;
    let start_count = 0;

    // if (!repos.length) {
    //   return <button onClick={this.fetchRepos.bind(this)}>load repos</button>
    // }

    //const mappedTweets = tweets.map(tweet => <li key={tweet.id}>{tweet.text}</li>)

    const mappedRepos = this.props.copy.map((repo, index) => {
      if (index >= start_offset && start_count < per_page) {
        start_count++;
        return  <a href={`/${repo.owner_username}/${repo.name}`.toLowerCase()} key={repo.id}><div className="col-md-4 box" ><img src={repo.photo_url} width="100%" className="img-responsive"/>{repo.name} by { repo.owner_username }</div></a>
      }

    })

    const mappedTags = this.props.tags.map(tag => {
      function toTitleCase(str)
      {
          return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
      }
      let titled = toTitleCase(tag.title)
      console.log('titled', titled)

      return <li key={tag.id}><a href="#" onClick={() => this.loadTags(tag.id)}>{titled}</a></li>


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
            Tags &nbsp;<a onClick={() => {this.none();}}>(clear)</a>
            {mappedTags}

          </ul>
        </div>
        <div className="col-md-10">
          <div className="row">
            {mappedRepos}
            <br/>

          </div>
          <div className="row">
            <div className="col-md-12 text-center">
              <Pagination className="user-pagination" bsSize="medium" maxButtons={10} first last next prev boundaryLinks items={pages} activePage={current_page} onSelect={this.changePage}/>
            </div>
          </div>
        </div>
      </div>

    </div>
  }

  changePage(page) {
    this.props.history.push('/?page=' + page);
  }
}
