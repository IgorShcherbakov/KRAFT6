#!/bin/bash

SCHEMA='{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
      "product_id": {
        "type": "string"
      },
      "name": {
        "type": "string"
      },
      "description": {
        "type": "string"
      },
      "price": {
        "type": "object",
        "properties": {
          "amount": {
            "type": "number"
          },
          "currency": {
            "type": "string"
          }
        },
        "required": ["amount", "currency"]
      },
      "category": {
        "type": "string"
      },
      "brand": {
        "type": "string"
      },
      "stock": {
        "type": "object",
        "properties": {
          "available": {
            "type": "integer"
          },
          "reserved": {
            "type": "integer"
          }
        },
        "required": ["available", "reserved"]
      },
      "sku": {
        "type": "string"
      },
      "tags": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "images": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "format": "uri"
            },
            "alt": {
              "type": "string"
            }
          },
          "required": ["url", "alt"]
        }
      },
      "specifications": {
        "type": "object",
        "properties": {
          "weight": {
            "type": "string"
          },
          "dimensions": {
            "type": "string"
          },
          "battery_life": {
            "type": "string"
          },
          "water_resistance": {
            "type": "string"
          }
        }
      },
      "created_at": {
        "type": "string",
        "format": "date-time"
      },
      "updated_at": {
        "type": "string",
        "format": "date-time"
      },
      "index": {
        "type": "string"
      },
      "store_id": {
        "type": "string"
      }
    },
    "required": [
      "product_id",
      "name",
      "description",
      "price",
      "category",
      "brand",
      "stock",
      "sku",
      "tags",
      "images",
      "specifications",
      "created_at",
      "updated_at",
      "index",
      "store_id"
    ]
}'

# Экранирование новой строки и других специальных символов
ESCAPED_SCHEMA=$(echo $SCHEMA | sed ':a;N;$!ba;s/\n/\\n/g' | sed 's/"/\\"/g')

curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
--data "{\"schema\": \"$ESCAPED_SCHEMA\", \"schemaType\": \"JSON\"}" \
http://schema-registry:8081/subjects/products-value/versions