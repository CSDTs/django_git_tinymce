import React from "react"

export default class Branches extends React.Component {


  //{this.props.branches.map((branch) => {
  //   return <li><a href="#">{branch}</a></li>
  // })}
  render() {
    console.log('this.props.branches', this.props.branches)
    if (!this.props.branches) {
      return <div>Loading...</div>
    }
    return (
      <div className="row">
        <div className="col-md-1 col-sm-3 col-xs-3">
           <div style={{margin: '0px 0px 10px 0px'}}>
            <div className="btn-group">
              <button type="button" className="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                <font style={{color: '#999'}} >branch:</font> <font> {this.props.branches} </font><span className="caret"></span>

              </button>
              <ul className="dropdown-menu">
                {(this.props.branches[0]) ? null : <li>None Created Yet</li> }
                {this.props.branches.map((branch, i) => <li key={i}><a href="#">{branch}</a></li>)}
              </ul>
            </div>

          </div>
        </div>
        <div className="col-md-offset-6 col-md-5 col-sm-offset-3 col-sm-6 col-xs-9" style={{padding: '0px'}}>
          {(this.props.is_owner || this.props.is_editor) &&
          <div style={{margin: '0px 0px 10px 0px'}} className="text-right">
            <div className="btn-group" role="group" aria-label="...">
              <a type="button" href={`createfolder`} className="btn btn-default button-link">Create Folder</a>
              <a type="button" href={`create`} className="btn btn-default button-link">Create New File</a>

              {/* <button type="button" className="btn btn-default disabled">Find Files</button> */}
            </div>
          </div>
        }
        </div>

    </div>
    )
  }
}
