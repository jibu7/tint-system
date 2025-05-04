const db = require('../db'); // Assuming db is your database connection module

async function getFormulaByCode(code) {
  console.log(`[DEBUG] DB Query - Getting formula with code: ${code}`);
  
  try {
    // This is a placeholder for your actual database query
    const query = 'SELECT * FROM formulas WHERE code = ?';
    console.log(`[DEBUG] Executing query: ${query} with params: [${code}]`);
    
    const formula = await db.query(query, [code]);
    console.log(`[DEBUG] DB returned formula:`, formula);
    
    if (formula && formula.length > 0) {
      // Now specifically log the colorant retrieval attempt
      const colorantQuery = 'SELECT * FROM colorants WHERE formula_id = ?';
      console.log(`[DEBUG] Executing colorant query: ${colorantQuery} with formula_id: [${formula[0].id}]`);
      
      const colorants = await db.query(colorantQuery, [formula[0].id]);
      console.log(`[DEBUG] DB returned colorants:`, colorants);
      
      // Attach colorants to formula
      formula[0].colorants = colorants;
      return formula[0];
    }
    return null;
  } catch (error) {
    console.error(`[ERROR] Database error getting formula: ${error.message}`);
    throw error;
  }
}

module.exports = {
  getFormulaByCode
};