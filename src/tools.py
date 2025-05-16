import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GraphQLTool:
    def __init__(self, api_url: str):
        """
        Initialize the GraphQL Tool.
        
        Args:
            api_url: URL of the GraphQL endpoint
        """
        self.api_url = api_url
        
    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query against the API.
        
        Args:
            query: The GraphQL query string
            variables: Optional variables for the query
            
        Returns:
            Dict containing the response data
        """
        if variables is None:
            variables = {}
            
        payload = {
            "query": query,
            "variables": variables
        }
        
        # Log the query
        logger.info(f"GraphQL Query: {query}")
        logger.info(f"Variables: {json.dumps(variables)}")
        
        response = requests.post(
            self.api_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            logger.error(f"GraphQL Error: {response.text}")
            return {"error": f"GraphQL request failed with status {response.status_code}"}
        
        result = response.json()
        
        if "errors" in result:
            logger.error(f"GraphQL Errors: {result['errors']}")
            return {"error": result["errors"]}
            
        return result
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Fetch the GraphQL schema.
        
        Returns:
            Dict containing the schema data
        """
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            queryType {
              name
            }
            mutationType {
              name
            }
            subscriptionType {
              name
            }
            types {
              kind
              name
              description
              fields {
                name
                description
                args {
                  name
                  description
                  type {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                        ofType {
                          kind
                          name
                        }
                      }
                    }
                  }
                  defaultValue
                }
                type {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
                isDeprecated
                deprecationReason
              }
              inputFields {
                name
                description
                type {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
                defaultValue
              }
              interfaces {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                    }
                  }
                }
              }
              enumValues {
                name
                description
                isDeprecated
                deprecationReason
              }
              possibleTypes {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                    }
                  }
                }
              }
            }
            directives {
              name
              description
              locations
              args {
                name
                description
                type {
                  kind
                  name
                  ofType {
                    kind
                    name
                    ofType {
                      kind
                      name
                      ofType {
                        kind
                        name
                      }
                    }
                  }
                }
                defaultValue
              }
            }
          }
        }
        """
        
        return self.execute_query(introspection_query)