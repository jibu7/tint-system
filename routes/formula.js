const express = require('express');
const router = express.Router();
const db = require('../db'); // Assuming db is a module for database operations

router.post('/search', async (req, res) => {
  const formulaCode = req.body.code;
  console.log(`[DEBUG] Searching for formula with code: ${formulaCode}`);
  
  try {
    // Assuming you have a database query here
    const formula = await db.getFormulaByCode(formulaCode);
    console.log(`[DEBUG] Formula search result:`, formula);
    
    // Check if formula exists but colorant data is missing
    if (formula) {
      console.log(`[DEBUG] Formula found. Colorant data:`, formula.colorants || 'No colorants array/object');
    } else {
      console.log(`[DEBUG] No formula found with code: ${formulaCode}`);
    }
    
    // Respond with the formula data or an appropriate message
    res.status(200).json(formula || { message: 'No formula found' });
  } catch (error) {
    console.error(`[ERROR] Error searching formula: ${error.message}`);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;