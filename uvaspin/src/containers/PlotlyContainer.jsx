import {React, Component} from 'react';
import { lab42Plot, lab36Plot } from '../components/Plots';

class PlotlyContainer extends Component {
    render() {
        return (
    <div>{this.props.plotly}</div>
        );
    }
}

export default PlotlyContainer;

