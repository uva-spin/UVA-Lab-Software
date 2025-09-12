/**
 * UI interaction functions for the UVA Lab System Panel
 */

/**
 * Toggle dropdown menu
 */
function toggleDropdown() {
    const dropdown = document.getElementById('control-dropdown');
    const dropdownContent = document.getElementById('dropdown-content');
    
    dropdown.classList.toggle('active');
    if (dropdown.classList.contains('active')) {
        dropdownContent.style.display = 'block';
    } else {
        dropdownContent.style.display = 'none';
    }
}

/**
 * Toggle floating action button menu
 */
function toggleFabMenu() {
    const fabMenu = document.querySelector('.fab-menu');
    const fab = document.querySelector('.fab');
    fabMenu.classList.toggle('active');
    fab.classList.toggle('active');
}

/**
 * Toggle sidebar visibility
 */
function toggleSidebar() {
    const sidebar = document.querySelector('.data-sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const dimmingOverlay = document.getElementById('dimming-overlay');
    
    sidebar.classList.toggle('active');
    toggleBtn.classList.toggle('active');
    dimmingOverlay.classList.toggle('active');
}

/**
 * Toggle section expansion
 * @param {string} sectionId - ID of the section to toggle
 */
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.querySelector('.section-header');
    const content = section.querySelector('.section-content');
    
    section.classList.toggle('expanded');
    if (section.classList.contains('expanded')) {
        content.style.maxHeight = content.scrollHeight + 'px';
    } else {
        content.style.maxHeight = '0';
    }
}

/**
 * Toggle main section expansion
 * @param {string} sectionId - ID of the main section to toggle
 */
function toggleMainSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.querySelector('.main-header');
    const content = section.querySelector('.main-content');
    const icon = header.querySelector('i');

    if (section.classList.contains('expanded')) {
        // Collapse the section
        content.style.maxHeight = '0';
        icon.className = 'fas fa-chevron-right';
        section.classList.remove('expanded');
        // Use setTimeout to ensure the transition completes before hiding
        setTimeout(() => {
            if (!section.classList.contains('expanded')) {
                content.style.display = 'none';
            }
        }, 300);
    } else {
        // Expand the section
        content.style.display = 'block';
        // Force a reflow to ensure display: block is applied
        content.offsetHeight;
        content.style.maxHeight = 'none';
        icon.className = 'fas fa-chevron-down';
        section.classList.add('expanded');
    }
}

/**
 * Toggle sub section expansion
 * @param {string} sectionId - ID of the sub section to toggle
 */
function toggleSubSection(sectionId) {
    const section = document.getElementById(sectionId);
    const header = section.querySelector('.sub-header');
    const content = section.querySelector('.sub-content');
    const icon = header.querySelector('i');

    if (section.classList.contains('expanded')) {
        // Collapse the section
        content.style.maxHeight = '0';
        icon.className = 'fas fa-chevron-right';
        section.classList.remove('expanded');
        // Use setTimeout to ensure the transition completes before hiding
        setTimeout(() => {
            if (!section.classList.contains('expanded')) {
                content.style.display = 'none';
            }
        }, 300);
    } else {
        // Expand the section
        content.style.display = 'block';
        // Force a reflow to ensure display: block is applied
        content.offsetHeight;
        content.style.maxHeight = 'none';
        icon.className = 'fas fa-chevron-down';
        section.classList.add('expanded');
    }
}

/**
 * Toggle parameter selection
 * @param {HTMLElement} parameterElement - The parameter element to toggle
 */
function toggleParameter(parameterElement) {
    parameterElement.classList.toggle('selected');
    handleParameterSelection();
}

/**
 * Handle parameter selection changes
 */
async function handleParameterSelection() {
    window.selectedKeys = Array.from(document.querySelectorAll('.parameter-item.selected'))
        .map(item => item.dataset.key);

    if (window.selectedKeys.length === 0) {
        updateEmptyChartDisplay();
        document.getElementById('chart-title').textContent = 'Select Data Entries';
        return;
    }

    const { data: dbData, availableKeys: dbAvailableKeys } = await fetchDataFromDB(window.selectedKeys);
    await updatePlot(dbData, window.selectedKeys, dbAvailableKeys);
}

/**
 * Select all data entries
 */
function selectAllData() {
    const parameterItems = document.querySelectorAll('.parameter-item');
    parameterItems.forEach(item => {
        item.classList.add('selected');
    });
    handleParameterSelection();
    Utils.showToast('All data entries selected!', 'success');
}

/**
 * Clear all data selections
 */
function clearAllData() {
    const parameterItems = document.querySelectorAll('.parameter-item');
    parameterItems.forEach(item => {
        item.classList.remove('selected');
    });
    handleParameterSelection();
    Utils.showToast('All data entries cleared!', 'info');
}

/**
 * Refresh data
 */
function refreshData() {
    updateFromDB();
    Utils.showToast('Data refreshed!', 'success');
}

/**
 * Get total column count from nested structure
 * @param {Array|Object} items - Items to count
 * @returns {number} - Total count
 */
function getTotalColumnCount(items) {
    if (Array.isArray(items)) {
        return items.length;
    } else {
        let total = 0;
        Object.values(items).forEach(item => {
            if (Array.isArray(item)) {
                total += item.length;
            } else {
                total += getTotalColumnCount(item);
            }
        });
        return total;
    }
}

/**
 * Create a sub-section element
 * @param {string} categoryName - Name of the category
 * @param {Array} columns - Array of column names
 * @returns {HTMLElement} - Created sub-section element
 */
function createSubSection(categoryName, columns) {
    const subSection = document.createElement('div');
    subSection.className = 'data-section sub-section';
    subSection.id = categoryName.toLowerCase().replace(/\s+/g, '-');

    const subHeader = document.createElement('div');
    subHeader.className = 'section-header sub-header';
    subHeader.onclick = () => toggleSubSection(subSection.id);
    subHeader.innerHTML = `
        <i class="fas fa-chevron-right"></i>
        <span>${categoryName}</span>
        <span class="section-count">${columns.length}</span>
    `;

    const subContent = document.createElement('div');
    subContent.className = 'section-content sub-content';
    // Ensure sub content is hidden by default
    subContent.style.display = 'none';
    subContent.style.maxHeight = '0';

    columns.forEach(columnName => {
        const parameterItem = document.createElement('div');
        parameterItem.className = 'parameter-item';
        parameterItem.dataset.key = columnName;
        parameterItem.onclick = () => toggleParameter(parameterItem);
        parameterItem.textContent = columnName;
        subContent.appendChild(parameterItem);
    });

    subSection.appendChild(subHeader);
    subSection.appendChild(subContent);
    return subSection;
}

/**
 * Create data selection sidebar from available columns
 * @param {Array} columns - Array of available column names
 */
function createDataSelectionSidebar(columns) {
    const sidebar = document.getElementById('data-sidebar');
    sidebar.innerHTML = ''; // Clear existing content

    console.log('Creating sidebar with columns:', columns);

    if (columns.length === 0) {
        sidebar.innerHTML = `
            <div class="error-container">
                <i class="fas fa-exclamation-triangle"></i>
                <p>No data columns available. Please check if the database is properly configured and contains data.</p>
                <button onclick="checkDatabaseStatus()" class="btn btn-primary">
                    <i class="fas fa-database"></i> Check Database Status
                </button>
            </div>
        `;
        return;
    }

    const nestedStructure = {
        'QT': {
            'Pressures': columns.filter(col => col.includes('pt')),
            'Flows': columns.filter(col => col.includes('fc')),
            // Exclude non-QT temperature-like fields
            'Temperatures': columns.filter(col => {
                const EXCLUDE_QT_TI = ['calibration_constant', 'polarization_std', 'polarization'];
                return col.includes('ti') && !col.includes('target_stick') && !EXCLUDE_QT_TI.includes(col);
            }),
            'Level Indicators': columns.filter(col => col.includes('li')),
            'Purity Meter': columns.filter(col => col.includes('ait'))
        },
        'Pressures': columns.filter(col => 
            !col.includes('pt') && 
            (col.includes('pressure') || col.includes('maxigauge') || col.includes('ivc'))
        ),
        'Temperatures': columns.filter(col => 
            !col.includes('ti') && 
            (col.includes('temperature') || col.includes('fridge') || col.includes('magnet') || col.includes('purifier') || col.includes('target_stick'))
        ),
        'Flows': columns.filter(col => 
            !col.includes('fc') && 
            col.includes('flow')
        ),
        // New NMR main section (no sub-groups)
        'NMR': (window.columnsByTable['NMR'] || [])
    };

    // Create nested dropdown structure
    Object.entries(nestedStructure).forEach(([mainCategory, subCategories]) => {
        const mainSection = document.createElement('div');
        mainSection.className = 'data-section main-category';
        // Ensure unique IDs for main categories
        mainSection.id = `main-${mainCategory.toLowerCase().replace(/\s+/g, '-')}`;

        const mainHeader = document.createElement('div');
        mainHeader.className = 'section-header main-header';
        mainHeader.onclick = () => toggleMainSection(mainSection.id);
        mainHeader.innerHTML = `
            <i class="fas fa-chevron-right"></i>
            <span>${mainCategory}</span>
            <span class="section-count">${getTotalColumnCount(subCategories)}</span>
        `;

        const mainContent = document.createElement('div');
        mainContent.className = 'section-content main-content';
        // Ensure main content is hidden by default
        mainContent.style.display = 'none';
        mainContent.style.maxHeight = '0';

        if (mainCategory === 'QT') {
            // QT has subcategories
            Object.entries(subCategories).forEach(([subCategory, subItems]) => {
                if (subItems.length > 0) {
                    // Use a unique prefix to avoid ID collisions with main categories
                    const subSection = createSubSection(subCategory, subItems, 'qt');
                    mainContent.appendChild(subSection);
                }
            });
        } else {
            // Other main categories are direct arrays - create parameter items directly
            if (subCategories.length > 0) {
                subCategories.forEach(columnName => {
                    const parameterItem = document.createElement('div');
                    parameterItem.className = 'parameter-item';
                    parameterItem.dataset.key = columnName;
                    parameterItem.onclick = () => toggleParameter(parameterItem);
                    parameterItem.textContent = columnName;
                    mainContent.appendChild(parameterItem);
                });
            }
        }

        mainSection.appendChild(mainHeader);
        mainSection.appendChild(mainContent);
        sidebar.appendChild(mainSection);
    });
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('control-dropdown');
    const dropdownContent = document.getElementById('dropdown-content');
    
    if (!dropdown.contains(event.target)) {
        dropdown.classList.remove('active');
        dropdownContent.style.display = 'none';
    }
});

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        toggleDropdown,
        toggleFabMenu,
        toggleSidebar,
        toggleSection,
        toggleMainSection,
        toggleSubSection,
        toggleParameter,
        handleParameterSelection,
        selectAllData,
        clearAllData,
        refreshData,
        getTotalColumnCount,
        createSubSection,
        createDataSelectionSidebar
    };
}
