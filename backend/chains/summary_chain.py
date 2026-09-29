from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from backend import config
from models.scholarship import Scholarship


def get_summary_chain():
    llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL,
        google_api_key=config.GEMINI_API_KEY
    )
    prompt = PromptTemplate.from_template(
        "Explain the following scholarship in one plain-English sentence for a student:\n"
        "Name: {name}\n"
        "Category: {category}\n"
        "Min CGPA: {min_cgpa}\n"
        "Max Family Income: {max_family_income}\n"
        "Eligible Academic Years: {eligible_years}\n"
        "Amount: {amount}\n"
        "Deadline: {deadline}\n"
        "Required Documents: {required_docs}"
    )
    return prompt | llm


def generate_scholarship_summary(scholarship: Scholarship) -> str:
    chain = get_summary_chain()
    result = chain.invoke({
        "name": scholarship.name,
        "category": scholarship.category,
        "min_cgpa": scholarship.min_cgpa,
        "max_family_income": scholarship.max_family_income,
        "eligible_years": scholarship.eligible_years,
        "amount": scholarship.amount,
        "deadline": scholarship.deadline,
        "required_docs": ", ".join(scholarship.required_docs)
    })
    return str(result.content).strip() if hasattr(result, "content") else str(result).strip()
