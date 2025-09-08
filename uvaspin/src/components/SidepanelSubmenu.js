import { React , useState } from 'react';
import SidepanelData from './SidepanelData';

function SidepanelSubmenu() {

    const [subnav, setSubnav] = useState(false);

    const showSubnav = () => setSubnav(!subnav);
    
    const handleColumnClick = (column) => {
        console.log(column);
    }

    return (
        <>
        <div onClick={showSubnav}>
            <h1>Columns</h1>
            {SidepanelData.map((item) => (
                <div key={item.title}>
                    <h2>{item.title}</h2>
                    {item.columns.map((column) => (
                        <div onClick={() => handleColumnClick(column)} key={column}>{column}</div>
                    ))}
                </div>
            ))}
        </div>
        </>
    )
}

export default SidepanelSubmenu;