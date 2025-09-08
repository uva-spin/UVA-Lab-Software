import { React , useState } from 'react';
import {Nav} from "react-bootstrap";
import SidepanelData from './SidepanelData';

function SidepanelSubmenu() {

    const [subnav, setSubnav] = useState(false);

    const showSubnav = () => setSubnav(!subnav);
    
    const handleColumnClick = (column) => {
        console.log(column);
    }
    return (
        <Nav className="sub-menu">
            <div className="sub-menu-content">
                <Nav.Item>
                    <span>Columns</span>
                    {SidepanelData.map((item) => (
                        <div key={item.title}>
                            <h2>{item.title}</h2>
                            {item.columns.map((column) => (
                                <div onClick={() => handleColumnClick(column)} key={column}>{column}</div>
                            ))}
                        </div>
                    ))}
                </Nav.Item>
            </div>
        </Nav>
    )
}

export default SidepanelSubmenu;