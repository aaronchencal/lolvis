import React, {Component} from 'react';
import {Switch, Route, Link, Redirect} from 'react-router-dom'
import Plot from 'react-plotly.js';
import './App.css'

const colors = ['2E382E', '50C9CE', '72A1E5', '9883E5', 'FF9FB9' ]

function toDT(secs) {
    var t = new Date(1970, 0, 1); // Epoch
    t.setSeconds(secs);
    return t;
}
class App extends Component {
  render() {
    return (
        <div className="App">
          <header className="App-header">
            <h1 className="App-title">lolvis</h1>
          </header>
          <Switch>
            <Route exact path="/" component={NameForm} />
            <Route path="/champions" component={ChampionForm}/>
            <Route path="/itemtl" component={ItemTimeline}/>
          </Switch>
        </div>
    );
  }
}

class ItemTimeline extends React.Component {
  constructor(props) {
    super(props);
    this.state = props.location.state
    this.state.rendered = false
    this.clicked = this.clicked.bind(this);
    fetch('/itemtl?sn=' + this.state.summoner + '&cid=' + this.state.cid).then(res => res.json()).then(data => {
      if(data.bad_request) {
        console.log("uh oh: bad request for this champion");
      }
       data.rendered = true
       data.currentItem = 0
        this.setState(data)
    });
  }


  clicked(curItem) {
    this.setState({currentItem:curItem})
  }

  render() {
    if(!this.state.rendered) {
      return <div/>
    }
    console.log(this.state);
    console.log("item: ")
    console.log(this.state.item)
    return (
      <div id="wrapper">
        <ItemList id="left" cback={this.clicked} item={this.state.item}/>
        <ItemPlot id="right" item={this.state.item} cur={this.state.currentItem}/>
      </div>
    );
  }
}

class ItemPlot extends React.Component {
  constructor(props) {
    super(props);
    var im = props.item
    im.unshift([0, 'All items', [], []])
    this.state = {item : props.item, cur : props.cur}
  }

   componentDidUpdate(prevProps) {
     if(prevProps.cur !== this.props.cur) {
       this.setState({ cur: this.props.cur });
     }
  }

  render() {
    var cur = parseInt(this.state.cur)

    var im = this.state.item.slice(1, this.state.item.length)
    const listItems = im.map((item, idx) =>
        ({
          x: item[2],
          type: 'box',
          mode: 'lines+markers',
          marker: {color: cur!==0 && idx === parseInt(this.state.cur) ? colors[1] : colors[2] },
          name: item[1] + " you"
        })
    );
    const clist = im.map((item, idx) =>
        ({
          x: item[3],
          type: 'box',
          mode: 'lines+markers',
          marker: {color: colors[3]},
          name: item[1] + " chally"
        })
    );
    console.log(clist);
    return <Plot
      data={cur===0 ? listItems : [listItems[cur-1], clist[cur-1]]}
      layout={
        { width: 1200,
          height: 600,
          title: this.state.item[cur][1],
          margin: {l:250},
          xaxis: {
            tickformat : "%M:%S"
          }
        }
      }
      staticPlot={true}
    />;
  }

}



class ItemList extends React.Component {
  constructor(props) {
    super(props);
    var im = props.item
    im = im.map((item) =>
      {
        item[2] = item[2].map((secs) => toDT(secs));
        item[3] = item[3].map((secs) => toDT(secs));
        return item;
      }
    );
    im.unshift([0, 'All items', []])

    this.state = {item: im}
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick(event) {
    this.props.cback(event.target.value)
  }

  render() {
    var im = this.state.item
    const listItems = im.map((item, idx) =>
    <li key={item.toString()}>
      <button value={idx} onClick={this.handleClick}>{item[1]}</button>
    </li>
    );
    console.log(listItems);

    return <ul> {listItems} </ul>;
  }

}

class ChampionForm extends React.Component {
  constructor(props) {
    super(props);
    console.log(props.location)
    this.state = props.location.state
  }

  render() {
    var champlist = this.state.value.map((lst) =>
    {
      return ( <li key={lst.toString()}>
          <Link to={{
            pathname: "/itemtl",
            state: {
              summoner: this.state.summoner,
              cid: lst[0]
            }
          }}> {lst[2]}: {lst[1]}</Link>
      </li>
      );
    });

    console.log(champlist);
    return  (
              <div className="Form">
                {champlist}
              </div>
            );

    }
}


class NameForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {value: '', show: true};

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
  }

  handleSubmit(event) {
    this.setState({show: false})
    console.log("nameform");
    fetch('/info?sn=' + this.state.value).then(res => res.json()).then(data => {
      console.log(data)
      this.setState({show: true})

      if(!data.bad_request) {
        this.props.history.push({
          pathname: '/champions',
          state: {value: data.champlist, summoner: this.state.value}
        })
      }
    });

    event.preventDefault();
  }

  render() {
    if (!this.state.show) {
      return <div/>
    }

    return (
      <div className="Form">
        <form onSubmit={this.handleSubmit}>
          <label>
            Summoner name:
            <input type="text" value={this.state.value} onChange={this.handleChange} />
          </label>
          <input type="submit" value="Submit" />
        </form>
      </div>
    );
  }
}

export default App;
