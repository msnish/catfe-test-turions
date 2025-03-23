from transformers import pipeline, set_seed
import sys
import torch
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logger import setup_logger

class GenerativeAI:
    def __init__(self, model_name="models/fine_tuned_gpt2", use_gpu=False):
        self.logger = setup_logger()
        self.logger.info(f"Initializing Generative AI with model: {model_name}")
        
        try:
            device = 0 if use_gpu and torch.cuda.is_available() else -1
            self.logger.info(f"Using {'GPU' if device == 0 else 'CPU'} for model inference.")
            
            self.generator = pipeline(
                "text-generation",
                model=model_name,
                device=device,
                framework="pt"
            )
            
            set_seed(42)
            self.logger.info(f"Successfully loaded model: {model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load Generative AI model: {str(e)}")
            raise

    def _truncate_prompt(self, prompt, max_tokens=100):
        """
        Truncate the prompt to a maximum number of tokens to avoid exceeding input limits.
        
        Args:
            prompt (str): The input prompt.
            max_tokens (int): Maximum number of tokens allowed.
        
        Returns:
            str: Truncated prompt.
        """
        tokens = self.generator.tokenizer(prompt, return_tensors="pt", truncation=False)["input_ids"]
        if tokens.shape[1] > max_tokens:
            self.logger.warning(f"Prompt exceeds {max_tokens} tokens ({tokens.shape[1]} tokens). Truncating...")
            truncated_tokens = tokens[:, :max_tokens]
            truncated_prompt = self.generator.tokenizer.decode(truncated_tokens[0], skip_special_tokens=True)
            return truncated_prompt
        return prompt

    def _generate_text(self, prompt, max_new_tokens=100, num_return_sequences=1):
        """
        Generate text using the fine-tuned GPT-2 model.
        
        Args:
            prompt (str): The input prompt for text generation.
            max_new_tokens (int): Number of new tokens to generate.
            num_return_sequences (int): Number of sequences to return.
        
        Returns:
            str: Generated text.
        """
        start_time = time.time()
        try:
            # Truncate prompt if too long
            prompt = self._truncate_prompt(prompt, max_tokens=100)
            # Tokenize the prompt to log its length
            input_ids = self.generator.tokenizer(prompt, return_tensors="pt", truncation=True)
            input_length = input_ids["input_ids"].shape[1]
            self.logger.debug(f"Input prompt length: {input_length} tokens")

            # Adjust max_new_tokens based on input length
            adjusted_max_new_tokens = max(20, max_new_tokens - (input_length - 100))
            self.logger.debug(f"Adjusted max_new_tokens: {adjusted_max_new_tokens}")

            outputs = self.generator(
                prompt,
                max_new_tokens=adjusted_max_new_tokens,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7,
                truncation=True,
                pad_token_id=self.generator.tokenizer.eos_token_id
            )
            generated_text = outputs[0]["generated_text"]
            elapsed_time = time.time() - start_time
            self.logger.info(f"Generated text for prompt: {prompt[:50]}... (took {elapsed_time:.2f} seconds)")
            return generated_text
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"Error generating text: {str(e)} (took {elapsed_time:.2f} seconds)")
            raise  # Re-raise the exception to ensure the caller handles it

    def generate_test_scenario(self, transaction_type, source_currency, destination_currency, amount, system_rules):
        # Optimize prompt by including only relevant rules
        relevant_rules = system_rules.get("transaction_limits", {}).get(transaction_type, {})
        limit = relevant_rules.get(source_currency, float('inf'))
        expected_result = "Success" if amount <= limit else "Failure"
        
        prompt = (
            f"Generate a detailed test scenario for a {transaction_type} transaction in a banking web app. "
            f"The transaction is from {source_currency} to {destination_currency} with an amount of {amount}. "
            f"Relevant system rules: {relevant_rules}. "
            f"The expected result is {expected_result}. "
            "Format the response as: 'Scenario: <description>. Expected result: <result>. Risks: <risks>.'"
        )
        
        generated_text = self._generate_text(prompt, max_new_tokens=100)
        
        if "Scenario:" not in generated_text:
            generated_text = (
                f"Scenario: Test {transaction_type} from {source_currency} to {destination_currency} with amount {amount}. "
                f"Expected result: {expected_result}. "
                f"Risks: {'Amount exceeds limit' if amount > limit else 'None'}."
            )
        
        return generated_text

    def generate_fraud_scenario(self, transaction, fraud_rules):
        amount = transaction["Amount"]
        destination = transaction["Destination Account"]
        
        risks = []
        if amount > fraud_rules["max_amount_per_transaction"]:
            risks.append(f"Amount {amount} exceeds max amount per transaction {fraud_rules['max_amount_per_transaction']}.")
        if destination in fraud_rules["suspicious_destinations"]:
            risks.append(f"Destination {destination} is flagged as suspicious.")
        expected_result = "Flag" if risks else "Pass"
        
        prompt = (
            f"Generate a fraud detection test scenario for a banking transaction. "
            f"The transaction has an amount of {amount} and destination account {destination}. "
            f"Fraud detection rules: {fraud_rules}. "
            f"The expected result is {expected_result}. "
            "Format the response as: 'Scenario: <description>. Risks: <risks>. Expected result: <result>.'"
        )
        
        generated_text = self._generate_text(prompt, max_new_tokens=100)
        
        if "Scenario:" not in generated_text:
            generated_text = (
                f"Scenario: Fraud detection for transaction with amount {amount} to {destination}. "
                f"Risks: {', '.join(risks) if risks else 'None'}. "
                f"Expected result: {expected_result}."
            )
        
        return generated_text

    def generate_customer_interaction_scenario(self, interaction_type, value, system_rules):
        if interaction_type == "login_attempts":
            max_attempts = system_rules["max_login_attempts"]
            login_attempts = value
            expected_result = "Success" if login_attempts <= max_attempts else "Failure"
            
            prompt = (
                f"Generate a customer interaction test scenario for a banking web app. "
                f"The customer has made {login_attempts} login attempts. "
                f"System rule: Maximum login attempts allowed is {max_attempts}. "
                f"The expected result is {expected_result}. "
                "Format the response as: 'Scenario: <description>. Expected result: <result>. Risks: <risks>.'"
            )
            
            generated_text = self._generate_text(prompt, max_new_tokens=100)
            
            if "Scenario:" not in generated_text:
                generated_text = (
                    f"Scenario: Customer login with {login_attempts} attempts. "
                    f"Expected result: {expected_result}. "
                    f"Risks: {'Too many login attempts' if login_attempts > max_attempts else 'None'}."
                )
            
            return generated_text
        return f"Scenario: Unknown interaction type {interaction_type}. Expected result: Unknown. Risks: None."

def generate_scenario_from_user_prompt(self, user_prompt, max_new_tokens=100):
    # Clean the prompt to ensure UTF-8 compatibility
    user_prompt = user_prompt.encode('utf-8', errors='ignore').decode('utf-8')
    
    # If the user prompt already requests a specific format, use it as-is
    if "Format the response as:" in user_prompt:
        prompt = user_prompt
    else:
        prompt = (
            f"{user_prompt} "
            "Format the response as: 'Scenario: <description>. Expected result: <result>. Risks: <risks>.'"
        )
    
    # Add an example to the prompt to guide the model
    prompt = (
        f"{prompt} For example: 'Scenario: Test Wire Transfer of $2000 from USD to JPY. Expected result: Success. Risks: None.'"
    )
    
    generated_text = self._generate_text(prompt, max_new_tokens=max_new_tokens)
    
    # Log the raw generated text for debugging
    self.logger.debug(f"Raw generated text: {generated_text}")
    
    # Validate the generated text format
    required_parts = ["Scenario:", "Expected result:", "Risks:"]
    # Check if the generated text is the prompt itself or lacks the required format
    if not generated_text or generated_text.strip() == prompt.strip() or not all(part in generated_text for part in required_parts):
        self.logger.warning(f"Generated text does not match expected format: {generated_text[:100]}...")
        # Fallback: Construct a basic scenario
        # Remove the format instruction from the user prompt for cleaner output
        description = user_prompt.split("Format the response as:")[0].strip()
        expected_result = "Failure" if "exceeds" in description.lower() else "Success"
        # Extract limit from the prompt if available
        import re
        limit_match = re.search(r"limit of \$([\d,]+)", description)
        risks = f"Amount exceeds daily limit of ${limit_match.group(1)}" if limit_match else "Amount exceeds daily limit"
        if not limit_match and not "exceeds" in description.lower():
            risks = "None"
        generated_text = (
            f"Scenario: {description}. Expected result: {expected_result}. Risks: {risks}."
        )
        self.logger.debug("Using fallback scenario due to invalid format.")
    
    # Ensure the output is UTF-8 encoded
    generated_text = generated_text.encode('utf-8', errors='replace').decode('utf-8')
    
    return generated_text

    def convert_scenario_to_training_text(self, scenario_text):
        """
        Convert a formatted scenario into free-form text suitable for training.
        
        Args:
            scenario_text (str): The formatted scenario (e.g., "Scenario: ... Expected result: ... Risks: ...")
        
        Returns:
            str: The free-form text for training.
        """
        if "Scenario:" in scenario_text and "Expected result:" in scenario_text and "Risks:" in scenario_text:
            parts = scenario_text.split(". ")
            if len(parts) >= 3:
                description = parts[0].replace("Scenario: ", "A user initiates a scenario where ")
                expected_result = parts[1].replace("Expected result: ", "The expected outcome is ")
                risks = parts[2].replace("Risks: ", "Potential risks include ")
                return f"{description}. {expected_result}. {risks}\n"
        # Fallback for non-standard format
        return f"A user initiates a scenario where {scenario_text.lower()}\n"