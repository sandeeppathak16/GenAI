from evaluator import evaluate

async def generate_report(dataset_version: str, prompt_version: str):
    results = evaluate(dataset_version=dataset_version, prompt_version=prompt_version)

    total = len(results)

    
