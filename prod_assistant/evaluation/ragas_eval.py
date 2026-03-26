import asyncio
from dotenv import load_dotenv

_model_loader = None

def _get_model_loader():
    global _model_loader
    if _model_loader is None:
        load_dotenv()
        from prod_assistant.utils.model_loader import ModelLoader
        _model_loader = ModelLoader()
    return _model_loader


def evaluate_context_precision(query, response, retrieved_context):
    try:
        from ragas import SingleTurnSample
        from ragas.llms import LangchainLLMWrapper
        from ragas.metrics import LLMContextPrecisionWithoutReference
        import grpc.experimental.aio as grpc_aio
        grpc_aio.init_grpc_aio()

        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_contexts=retrieved_context,
        )

        async def main():
            llm = _get_model_loader().load_llm()
            evaluator_llm = LangchainLLMWrapper(llm)
            context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)
            result = await context_precision.single_turn_ascore(sample)
            return result

        return asyncio.run(main())
    except Exception as e:
        return e

def evaluate_response_relevancy(query, response, retrieved_context):
    try:
        from ragas import SingleTurnSample
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.metrics import ResponseRelevancy
        import grpc.experimental.aio as grpc_aio
        grpc_aio.init_grpc_aio()

        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_contexts=retrieved_context,
        )

        async def main():
            llm = _get_model_loader().load_llm()
            evaluator_llm = LangchainLLMWrapper(llm)
            embedding_model = _get_model_loader().load_embeddings()
            evaluator_embeddings = LangchainEmbeddingsWrapper(embedding_model)
            scorer = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
            result = await scorer.single_turn_ascore(sample)
            return result

        return asyncio.run(main())
    except Exception as e:
        return e