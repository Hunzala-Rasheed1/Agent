import os
import json
import logging
from typing import Dict, Any

from langchain.chat_models import AzureChatOpenAI
from langchain.chains import LLMChain
from azure.core.credentials import AzureKeyCredential

from src.tools import GraphQLTool
from src.prompts import NL_TO_GRAPHQL_PROMPT, ANSWER_PROMPT

logger = logging.getLogger(__name__)

class GraphQLAgent:
    def __init__(self, graphql_url: str, openai_api_key: str, openai_api_version: str, openai_api_endpoint: str):
        """
        Initialize the GraphQL Agent.
        
        Args:
            graphql_url: URL of the GraphQL endpoint
            openai_api_key: OpenAI API key
            openai_api_version: OpenAI API version
            openai_api_endpoint: OpenAI API endpoint
        """
        self.graphql_tool = GraphQLTool(graphql_url)
        
        self.llm = AzureChatOpenAI(
            azure_deployment="gpt-4o",  # Use the appropriate deployment
            openai_api_version=openai_api_version,
            azure_endpoint=openai_api_endpoint,
            api_key=openai_api_key,
            temperature=0,  # Keep deterministic for queries
        )
        
        self.nl_to_graphql_chain = LLMChain(
            llm=self.llm,
            prompt=NL_TO_GRAPHQL_PROMPT,
            verbose=True
        )
        
        self.answer_chain = LLMChain(
            llm=self.llm,
            prompt=ANSWER_PROMPT,
            verbose=True
        )
        
        # Cache the schema to avoid repeated calls
        self._schema = None
        
    def get_fallback_schema_description(self) -> str:
        """
        Provides a fallback schema description when introspection fails.
        """
        return """
        GraphQL Schema for JobLogic API:
        
        Type: Job
        Fields:
          - id: Int!
          - jobNumber: String!
          - description: String!
          - appointmentDate: DateTime
          - customerId: Int!
          - siteId: Int!
          - statusStringId: String!
          - statusDescription: String!
          - customer: Customer
          - site: Site
          - jobType: JobType
          - priority: Priority
          
        Type: Customer
        Fields:
          - id: Int!
          - name: String!
          - address1: String
          - address2: String
          - address3: String
          - address4: String
          - postcode: String
          - contact: String
          - emailAddress: String
          - telephone: String
        
        Type: Site
        Fields:
          - id: Int!
          - name: String!
          - customerId: Int!
          - address1: String
          - address2: String
          - address3: String
          - address4: String
          - postcode: String
          - telephone: String
          - contactName: String
          - emailAddress: String
        
        Type: Asset
        Fields:
          - id: Int!
          - uniqueId: UUID!
          - description: String!
          - serialNumber: String
          - location: String
          - customerId: Int!
          - siteId: Int!
          - customer: Customer
          - site: Site
        
        Type: JobListResult
        Fields:
          - items: [Job!]!
          - totalCount: Int!
        
        Type: CustomerListResult
        Fields:
          - items: [Customer!]!
          - totalCount: Int!
        
        Type: SiteListResult
        Fields:
          - items: [Site!]!
          - totalCount: Int!
        
        Type: AssetListResult
        Fields:
          - items: [Asset!]!
          - totalCount: Int!
        
        Query:
          - job(id: Int!): Job
          - jobs(searchTerm: String, customerId: Int, siteId: Int, fromDate: DateTime, toDate: DateTime, pageSize: Int! = 20, pageIndex: Int! = 1, orderBy: JobOrderBy! = JOB_NUMBER_ASC): JobListResult!
          - customer(id: Int!): Customer!
          - customers(searchTerm: String, pageSize: Int! = 20, pageIndex: Int! = 1, orderBy: CustomerOrderBy! = NAME_ASC): CustomerListResult!
          - site(id: Int!): Site!
          - sites(searchTerm: String, customerId: Int, pageSize: Int! = 20, pageIndex: Int! = 1, orderBy: SiteOrderBy! = NAME_ASC): SiteListResult!
          - asset(id: Int!): Asset
          - assets(searchTerm: String, siteId: Int, pageSize: Int! = 20, pageIndex: Int! = 0, orderBy: SiteAsset_OrderBy! = SERIALNUMBER_DESC): AssetListResult!
        
        Enum: JobOrderBy
        Values:
          - JOB_NUMBER_ASC
          - JOB_NUMBER_DESC
          - APPOINTMENT_DATE_ASC
          - APPOINTMENT_DATE_DESC
          - CUSTOMER_NAME_ASC
          - CUSTOMER_NAME_DESC
        
        Enum: CustomerOrderBy
        Values:
          - NAME_ASC
          - NAME_DESC
          - ADDRESS1_ASC
          - ADDRESS1_DESC
          - POSTCODE_ASC
          - POSTCODE_DESC
        
        Enum: SiteOrderBy
        Values:
          - NAME_ASC
          - NAME_DESC
          - ADDRESS1_ASC
          - ADDRESS1_DESC
          - POSTCODE_ASC
          - POSTCODE_DESC
        """
    
    def get_schema_description(self) -> str:
        """
        Get a simplified description of the GraphQL schema.
        
        Returns:
            String representation of the schema
        """
        try:
            if not self._schema:
                schema_result = self.graphql_tool.get_schema()
                self._schema = schema_result
                
            if "data" not in self._schema or "__schema" not in self._schema.get("data", {}):
                logger.warning("Schema retrieval failed, using fallback schema")
                return self.get_fallback_schema_description()
                
            schema_data = self._schema["data"]["__schema"]
            
            # Format the schema in a way that's useful for the LLM
            types = schema_data["types"]
            # Filter out introspection types
            filtered_types = [t for t in types if not t["name"].startswith("__") and t["kind"] in ["OBJECT", "ENUM", "INPUT_OBJECT"]]
            
            schema_str = "GraphQL Schema Types:\n\n"
            
            for t in filtered_types:
                schema_str += f"Type: {t['name']} ({t['kind']})\n"
                if t["description"]:
                    schema_str += f"Description: {t['description']}\n"
                    
                # Add fields for object types
                if t["fields"]:
                    schema_str += "Fields:\n"
                    for field in t["fields"]:
                        field_type = field["type"]
                        type_str = self._format_type(field_type)
                        schema_str += f"  - {field['name']}: {type_str}\n"
                        if field["description"]:
                            schema_str += f"    Description: {field['description']}\n"
                            
                # Add enum values for enum types
                if t["enumValues"]:
                    schema_str += "Values:\n"
                    for value in t["enumValues"]:
                        schema_str += f"  - {value['name']}\n"
                        
                # Add input fields for input object types
                if t["inputFields"]:
                    schema_str += "Input Fields:\n"
                    for field in t["inputFields"]:
                        field_type = field["type"]
                        type_str = self._format_type(field_type)
                        schema_str += f"  - {field['name']}: {type_str}\n"
                        if field["description"]:
                            schema_str += f"    Description: {field['description']}\n"
                            
                schema_str += "\n"
                
            return schema_str
        except Exception as e:
            logger.warning(f"Error retrieving schema: {str(e)}")
            return self.get_fallback_schema_description()
    
    def _format_type(self, type_info: Dict[str, Any]) -> str:
        """
        Format a GraphQL type into a string representation.
        
        Args:
            type_info: Type information from schema
            
        Returns:
            String representation of the type
        """
        kind = type_info["kind"]
        name = type_info["name"]
        
        if kind == "NON_NULL":
            ofType = type_info["ofType"]
            return f"{self._format_type(ofType)}!"
        elif kind == "LIST":
            ofType = type_info["ofType"]
            return f"[{self._format_type(ofType)}]"
        else:
            return name or kind
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language question and return an answer.
        
        Args:
            question: Natural language question from the user
            
        Returns:
            Dict with the answer and additional information
        """
        try:
            # Get schema description
            schema_description = self.get_schema_description()
            
            # Convert question to GraphQL query
            graphql_response = self.nl_to_graphql_chain.run({
                "schema": schema_description,
                "question": question
            })
            
            # Clean up the query by removing markdown formatting
            graphql_query = graphql_response.strip()
            graphql_query = graphql_query.replace('```graphql', '').replace('```', '').strip()
            logger.info(f"Generated GraphQL Query: {graphql_query}")
            
            # Execute the query
            result = self.graphql_tool.execute_query(graphql_query)
            
            # Format the answer
            answer = self.answer_chain.run({
                "question": question,
                "graphql_query": graphql_query,
                "result": json.dumps(result, indent=2)
            })
            
            return {
                "answer": answer,
                "graphql_query": graphql_query,
                "raw_result": result
            }
            
        except Exception as e:
            logger.exception("Error in GraphQL agent")
            return {
                "answer": f"I encountered an error: {str(e)}",
                "error": str(e)
            }