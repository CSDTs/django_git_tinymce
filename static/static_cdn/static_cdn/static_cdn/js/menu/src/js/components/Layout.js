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
    clear: store.tags.clear,
    name: store.tags.name,
    //page: Number(store.routing.locationBeforeTransitions.query.page) || 1
  };
})



export default class Layout extends React.Component {




  constructor(props) {
    super(props);
    this.changePage = this.changePage.bind(this);
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

      })
      .catch((err) => {
        this.owner = "unknown"
      })
    return this.owner
  }

  loadTags(id) {

    const filtered_tags = this.props.tags.filter((tag) => {
      return tag.id == id
    })

    name = filtered_tags[0].title
    this.props.dispatch({type: "CHANGE_NAME", payload: name})

    const repos_filtered = this.props.repos.filter((repo) => {
      const okay = filtered_tags.map(tag_repo => {
        const okay3 = tag_repo.repos.filter((tag) => {

          return tag == repo.id
        })

        return okay3
      })

      if (okay[0].length == 0) {
        return false
      }
      else {
        return true
      }
    })

    this.props.dispatch({type: "FILTER_REPOS", payload: repos_filtered})

  }

  none() {
    this.props.dispatch({type: "FILTER_REPOS", payload: this.props.repos})
  }



  render() {


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
    let search = getParameterByName('search') || null
    if (search) {
      search = search.toLowerCase()
    }
    const { user, repos, fetching, fetched, tags } = this.props;
    const per_page = 30;
    const pages = Math.ceil(this.props.copy.length / per_page );
    const current_page = query
    const start_offset = (current_page - 1) * per_page;
    let start_count = 0;

    // if (!repos.length) {
    //   return <button onClick={this.fetchRepos.bind(this)}>load repos</button>
    // }

    //const mappedTweets = tweets.map(tweet => <li key={tweet.id}>{tweet.text}</li>)
    let mappedRepos = null
    if (search) {
      const filteredRepos = this.props.copy.filter((repo) => {
        if (`${repo.name}`.toLowerCase().includes(search))
          return true
        if (`${repo.owner_username}`.toLowerCase().includes(search))
          return true
        if (`${repo.description}`.toLowerCase().includes(search))
          return true
        return false
      })
      mappedRepos = filteredRepos.map((repo, index) => {
        if (index >= start_offset && start_count < per_page) {
          start_count++;
          return  <a href={`/${repo.owner_username}/${repo.slug}`.toLowerCase()} key={repo.id}><div className="col-md-4 box" ><img src={repo.photo_url} width="100%" className="img-responsive"/>{repo.name} by { repo.owner_username }</div></a>
        }

      })

    }
    else {

        mappedRepos = this.props.copy.map((repo, index) => {
          if (index >= start_offset && start_count < per_page) {
            start_count++;
            return  <a href={`/${repo.owner_username}/${repo.slug}`.toLowerCase()} key={repo.id}><div className="col-md-4 box" ><img src={repo.photo_url} width="100%" className="img-responsive"/>{repo.name} by { repo.owner_username }</div></a>
          }

        })
    }




    const mappedTags = this.props.tags.map(tag => {
      function toTitleCase(str)
      {
          return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
      }
      let titled = toTitleCase(tag.title)


      return <li key={tag.id}><a href="#" onClick={() => {this.loadTags(tag.id);this.props.dispatch({type:"SHOW_CLEAR", payload: true});}}>{titled}</a></li>


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
            Tags &nbsp;{this.props.clear ? <a onClick={() => {this.none();this.props.dispatch({type:"SHOW_CLEAR", payload: false});this.props.dispatch({type: "CHANGE_NAME", payload: null});}}>(clear)</a> : null }
            {mappedTags}

          </ul>
        </div>
        <div className="col-md-10">
          <div className="row">
            {(this.props.name) ? (search)? <h2>Showing repos with tag "{name}" and search term "{search}" <a href="/">(clear)</a>:</h2>: <h2>Showing repos with tag "{name}" <a href="#" onClick={() => {this.none();this.props.dispatch({type:"SHOW_CLEAR", payload: false});this.props.dispatch({type: "CHANGE_NAME", payload: null});}}>(clear)</a>:</h2>: null}
            {(search && ! this.props.name) ? <h2>Showing repos that match search term "{search}" <a href="/">(clear)</a>:</h2>: null}
            {mappedRepos}
            <br/>

          </div>
          <div className="row">
            <div className="col-md-12 text-center">
              {(pages > 1) ? <Pagination className="user-pagination" bsSize="medium" maxButtons={10} first last next prev boundaryLinks items={pages} activePage={current_page} onSelect={this.changePage}/> : null}
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
