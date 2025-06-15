"""
Utilities for visualizing entity mapping results.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.entity_mapper.schema import MappingResult


def generate_html_visualization(
    mapping_results: List[MappingResult],
    output_path: Union[str, Path]
) -> None:
    """
    Generate an HTML visualization of entity mapping results.
    
    Args:
        mapping_results: List of mapping results
        output_path: Path to save the HTML file
    """
    # Convert mapping results to JSON for JavaScript
    mapping_data_json = json.dumps([r.dict() for r in mapping_results])
    
    # Create HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entity Mapping Visualization</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        h1, h2 {{
            color: #333;
        }}
        .card {{
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #fff;
        }}
        .card-title {{
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        .card-content {{
            display: flex;
            flex-wrap: wrap;
        }}
        .entity-info {{
            flex: 1;
            min-width: 300px;
            padding: 10px;
        }}
        .entity-info h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .mapping-result {{
            flex: 1;
            min-width: 300px;
            padding: 10px;
        }}
        .mapping-info {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        .mapping-arrow {{
            font-size: 24px;
            margin: 0 10px;
            color: #3498db;
        }}
        .confidence {{
            background-color: #f39c12;
            color: white;
            border-radius: 3px;
            padding: 3px 5px;
            font-size: 12px;
            margin-left: 10px;
        }}
        .name-change {{
            background-color: #e74c3c;
            color: white;
            border-radius: 3px;
            padding: 3px 5px;
            font-size: 12px;
            margin-left: 10px;
        }}
        .no-mapping {{
            color: #e74c3c;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Entity Mapping Visualization</h1>
        
        <div id="summary">
            <h2>Summary</h2>
            <div class="card">
                <div id="summary-stats"></div>
                <div id="summary-chart"></div>
            </div>
        </div>
        
        <div id="mapping-results">
            <h2>Mapping Results</h2>
            <div id="entity-cards"></div>
        </div>
    </div>

    <script>
        // Load mapping data
        const mappingResults = {mapping_data_json};
        
        // Generate summary statistics
        function generateSummary() {{
            const totalEntities = mappingResults.length;
            const mappedEntities = mappingResults.filter(r => r.mapped_entity_id).length;
            const nameChanges = mappingResults.filter(r => r.name_change_detected).length;
            
            const summaryHtml = `
                <table>
                    <tr>
                        <th>Total Entities</th>
                        <th>Mapped Entities</th>
                        <th>Mapping Rate</th>
                        <th>Name Changes Detected</th>
                    </tr>
                    <tr>
                        <td>${{totalEntities}}</td>
                        <td>${{mappedEntities}}</td>
                        <td>${{(mappedEntities / totalEntities * 100).toFixed(1)}}%</td>
                        <td>${{nameChanges}}</td>
                    </tr>
                </table>
            `;
            
            document.getElementById('summary-stats').innerHTML = summaryHtml;
        }}
        
        // Generate entity cards
        function generateEntityCards() {{
            const cardsContainer = document.getElementById('entity-cards');
            let cardsHtml = '';
            
            mappingResults.forEach(result => {{
                const originalEntity = result.original_entity;
                const isMapped = !!result.mapped_entity_id;
                const hasNameChange = result.name_change_detected;
                
                let mappingHtml = '';
                if (isMapped) {{
                    mappingHtml = `
                        <div class="mapping-info">
                            <strong>${{originalEntity.name}}</strong>
                            <div class="mapping-arrow">→</div>
                            <strong>${{result.mapped_entity_name}}</strong>
                            <span class="confidence">Confidence: ${{(result.confidence * 100).toFixed(1)}}%</span>
                            ${{hasNameChange ? '<span class="name-change">Name Change</span>' : ''}}
                        </div>
                    `;
                    
                    if (hasNameChange && result.name_change) {{
                        mappingHtml += `
                            <div>
                                <strong>Name Change:</strong> ${{result.name_change.previous_name}} → ${{result.name_change.current_name}}<br>
                                ${{result.name_change.change_date ? `<strong>Date:</strong> ${{result.name_change.change_date}}<br>` : ''}}
                                ${{result.name_change.change_reason ? `<strong>Reason:</strong> ${{result.name_change.change_reason}}` : ''}}
                            </div>
                        `;
                    }}
                }} else {{
                    mappingHtml = `
                        <div class="no-mapping">
                            <strong>No matching entity found in database</strong>
                        </div>
                    `;
                }}
                
                cardsHtml += `
                    <div class="card">
                        <h3 class="card-title">${{originalEntity.name}} <small>(${{originalEntity.type}})</small></h3>
                        <div class="card-content">
                            <div class="entity-info">
                                <h3>Extracted Information</h3>
                                <p><strong>Type:</strong> ${{originalEntity.type}}</p>
                                ${{originalEntity.aliases && originalEntity.aliases.length > 0 ? `<p><strong>Aliases:</strong> ${{originalEntity.aliases.join(', ')}}</p>` : ''}}
                                ${{originalEntity.description ? `<p><strong>Description:</strong> ${{originalEntity.description}}</p>` : ''}}
                                <!-- Add additional entity properties as needed -->
                            </div>
                            <div class="mapping-result">
                                <h3>Mapping Result</h3>
                                ${{mappingHtml}}
                            </div>
                        </div>
                    </div>
                `;
            }});
            
            cardsContainer.innerHTML = cardsHtml;
        }}
        
        // Initialize visualization
        document.addEventListener('DOMContentLoaded', () => {{
            generateSummary();
            generateEntityCards();
        }});
    </script>
</body>
</html>
"""
    
    # Write HTML to file
    with open(output_path, "w") as f:
        f.write(html_content)
