document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const generateBtn = document.getElementById('generateBtn');
    const apiKeyInput = document.getElementById('apiKey');
    const spinnerContainer = document.getElementById('spinnerContainer');
    const mealResult = document.getElementById('mealResult');
    const mealNameEl = document.getElementById('mealName');
    const ingredientsEl = document.getElementById('ingredients');
    const instructionsEl = document.getElementById('instructions');
    
    // Add event listener to the button
    generateBtn.addEventListener('click', generateMeal);
    
    async function generateMeal() {
        // Show spinner, hide previous results
        spinnerContainer.style.display = 'block';
        mealResult.style.display = 'none';
        generateBtn.disabled = true;
        
        // Get API key if provided
        const apiKey = apiKeyInput.value.trim();
        
        try {
            // Call the API
            const response = await fetch('/generate-meal', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiKey || null
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to generate meal');
            }
            
            // Parse and display the meal
            const meal = await response.json();
            displayMeal(meal);
            
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            // Hide spinner, re-enable button
            spinnerContainer.style.display = 'none';
            generateBtn.disabled = false;
        }
    }
    
    function displayMeal(meal) {
        // Set meal name
        mealNameEl.textContent = meal.meal_name;
        
        // Clear and populate ingredients
        ingredientsEl.innerHTML = '';
        meal.ingredients.forEach(ingredient => {
            const li = document.createElement('li');
            li.textContent = ingredient;
            ingredientsEl.appendChild(li);
        });
        
        // Set instructions
        instructionsEl.textContent = meal.instructions;
        
        // Show the result container
        mealResult.style.display = 'block';
    }
});