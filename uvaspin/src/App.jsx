import { React } from 'react'
import { Banner } from './components/Banner';
import { SidePanel } from './components/Sidepanel';
import { PlotlyContainer } from './containers/PlotlyContainer';
import { lab42Button, lab36Button, sidePanelButton } from './components/Buttons';
import './App.css'

function UVASpin() {
  return (
    <Banner title="UVA Polarized Target Group Labs System Panel" lab42Button={lab42Button} lab36Button={lab36Button} sidePanelButton={sidePanelButton} />,
    <SidePanel />,
    <PlotlyContainer />
  )
}

export default UVASpin
