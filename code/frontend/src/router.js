import React from 'react';
import { BrowserRouter as Router, Route } from 'react-router-dom'
import Navigation from './components/Navigation/Navigation';
import Landing from './views/Landing/Landing';
import Unkown from './views/Unkown/Unkown';
import Known from './views/Known/Known';

export default () => (
  <div style={{ display: 'flex' }}>
    <Router>
      <Navigation />
      <Route exact path="/unkown" component={Unkown}/>
      <Route exact path="/known" component={Known}/>
      <Route exact path="/" component={Landing}/>
    </Router>
  </div>
)