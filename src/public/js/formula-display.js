document.addEventListener('DOMContentLoaded', function() {
    // Debug flag - set to true for console logging
    const DEBUG = true;

    function searchFormula(code) {
        fetch(`/api/search/${encodeURIComponent(code)}`)
        .then(response => response.json())
        .then(data => {
            if (DEBUG) {
                console.log('[DEBUG] Formula API response received:', data);
            }
            if (!document.getElementById('formula-results')) {
                console.error('[DEBUG] CRITICAL: resultsContainer element not found in DOM before calling displayFormulaData!');
            }
            displayFormulaData(data);
        })
        .catch(error => {
            console.error('[DEBUG] Error fetching formula data:', error);
        });
    }

    function displayFormulaData(formula) {
        const resultsContainer = document.getElementById('formula-results'); 
        
        if (DEBUG) console.log('[DEBUG] Entering displayFormulaData function.');
        
        if (!resultsContainer) {
            console.error('[DEBUG] CRITICAL: resultsContainer element not found inside displayFormulaData!');
            return;
        } else {
            if (DEBUG) console.log('[DEBUG] resultsContainer element found.');
        }
        
        if (!formula) {
            if (DEBUG) console.error('[DEBUG] formula data is null or undefined.');
            resultsContainer.innerHTML = '<p class="error">Error: Received invalid formula data.</p>';
            return;
        }
        
        if (DEBUG) console.log('[DEBUG] Preparing basic formula info HTML.');
        let htmlContent = `
            <h3>Color Code: ${formula.color_code || 'N/A'}</h3>
            <p>Color Series: ${formula.color_series || 'N/A'}</p>
            <p>Color Card: ${formula.color_card || 'N/A'}</p>
            <p>Paint Type: ${formula.paint_type || 'N/A'}</p>
            <p>Base Paint: ${formula.base_paint || 'N/A'}</p>
        `;
        
        if (DEBUG) console.log('[DEBUG] Basic info HTML prepared. Preparing colorants section.');
        htmlContent += '<h3>Colorants Required:</h3>';
        
        if (DEBUG) {
            console.log('[DEBUG] Checking formula.colorant_details:', formula.colorant_details);
            console.log('[DEBUG] Type of formula.colorant_details:', typeof formula.colorant_details);
            console.log('[DEBUG] Is Array:', Array.isArray(formula.colorant_details));
            if (Array.isArray(formula.colorant_details)) {
                console.log('[DEBUG] Array Length:', formula.colorant_details.length);
            }
        }
        
        const hasColorants = formula.colorant_details && Array.isArray(formula.colorant_details) && formula.colorant_details.length > 0;
        
        if (DEBUG) console.log('[DEBUG] hasColorants check result:', hasColorants);
        
        if (hasColorants) {
            if (DEBUG) console.log('[DEBUG] Colorant data found. Building table HTML.');
            
            htmlContent += '<table class="colorant-table">';
            htmlContent += '<thead><tr><th>Colorant</th><th>Weight (g)</th><th>Volume (ml)</th></tr></thead>';
            htmlContent += '<tbody>';
            
            try {
                formula.colorant_details.forEach((colorant, index) => {
                    if (DEBUG) console.log(`[DEBUG] Processing colorant item ${index}:`, colorant);
                    htmlContent += `<tr>
                        <td>${colorant.colorant_name || 'Unnamed'}</td>
                        <td>${colorant.weight_g != null ? colorant.weight_g.toFixed(4) : 'N/A'}</td> 
                        <td>${colorant.volume_ml != null ? colorant.volume_ml.toFixed(4) : 'N/A'}</td>
                    </tr>`;
                });
                if (DEBUG) console.log('[DEBUG] Finished processing colorant items.');
            } catch (loopError) {
                console.error('[DEBUG] Error during colorant loop:', loopError);
                htmlContent += '<tr><td colspan="3">Error processing colorant data.</td></tr>';
            }
            
            htmlContent += '</tbody></table>';
            if (DEBUG) console.log('[DEBUG] Colorant table HTML built.');
        } else {
            if (DEBUG) console.warn('[DEBUG] No valid colorant_details found in formula response.');
            
            htmlContent += '<p>No specific colorant data available for this code.</p>';
            
            if (DEBUG) {
                htmlContent += `<div class="debug-info" style="background:#ffe; border:1px solid #aa0; padding:10px; margin-top:20px;">
                    <h4>Debug Information (No Colorants)</h4>
                    <p>Formula object received but no valid 'colorant_details' array found.</p>
                    <p>Available formula properties: ${Object.keys(formula).join(', ')}</p>
                    <pre>Raw Response:\n${JSON.stringify(formula, null, 2)}</pre>
                </div>`;
            }
        }
        
        if (DEBUG) console.log('[DEBUG] Final HTML content prepared. Setting innerHTML.');
        try {
            resultsContainer.innerHTML = htmlContent;
            if (DEBUG) console.log('[DEBUG] innerHTML set successfully.');
        } catch (renderError) {
            console.error('[DEBUG] CRITICAL: Error setting innerHTML:', renderError);
            resultsContainer.innerHTML = `<p class="error">Error displaying results. Check console.</p>`;
        }
    }
});