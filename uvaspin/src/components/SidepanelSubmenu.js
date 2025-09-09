import { React , useState } from 'react';
import SidepanelData from './SidepanelData';

function SidepanelSubmenu() {

    const [sidePanelSubmenu, setSidePanelSubmenu] = useState(false);

    const showSubnav = () => setSidePanelSubmenu(!sidePanelSubmenu);
    
    const handleColumnClick = (column) => {
        console.log(column);
    }

    return (
        <>
        <div className='side-panel-submenu'>
            <div className='side-panel-submenu-content'>
                <div>
                    <span>Columns</span>
                </div>
                {SidepanelData.map((item) => (
                    <div key={item.title}>
                        <h2>{item.title}</h2>
                        {item.columns.map((column) => (
                            <div onClick={() => handleColumnClick(column)} key={column}>{column}</div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
        </>
    )
}

export default SidepanelSubmenu;