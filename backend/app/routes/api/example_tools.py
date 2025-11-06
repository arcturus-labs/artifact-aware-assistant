from .conversation import Artifact, Tool


def get_listing(address):
    content = f"""\
{{
    "address": "{address}",
    "city": "Cedar Rapids",
    "state": "IA",
    "zip": "52402",
    "price": 185000,
    "beds": 3,
    "baths": 2,
    "sqft": 1450,
    "lot_size": 0.25,
    "year_built": 1978,
    "description": "Charming ranch-style home in established neighborhood. Updated kitchen with new appliances. Finished basement, attached 2-car garage, fenced backyard with mature trees. Close to schools and shopping.",
    "features": [           
        "Central air",
        "Forced air heating",
        "Hardwood floors",
        "Updated kitchen",
        "Finished basement",
        "Attached garage",
        "Fenced yard"
    ],
}}
"""
    
    artifact = Artifact(
        identifier="18bacG4a",
        type="application/json", 
        title=address, 
        content=content)
    return str(artifact)

def get_comparables(address):
    artifact = Artifact(
        identifier="3baf9f83", 
        type="application/json", 
        title=f"{address} Comparables", 
        content="""\
[
    {
        "address": "738 Maple Street",
        "city": "Cedar Rapids", 
        "state": "IA",
        "price": 179900,
        "beds": 3,
        "baths": 2,
        "sqft": 1400,
        "year_built": 1975,
        "last_sold": {
            "date": "2020-03-15",
            "price": 165000
        },
        "distance_miles": 0.1,
        "zestimate": 183000
    },
    {
        "address": "755 Oak Drive",
        "city": "Cedar Rapids",
        "state": "IA", 
        "price": 192000,
        "beds": 3,
        "baths": 2.5,
        "sqft": 1500,
        "year_built": 1980,
        "last_sold": {
            "date": "2021-08-01",
            "price": 180000
        },
        "distance_miles": 0.3,
        "zestimate": 195000
    },
    {
        "address": "729 Elm Court",
        "city": "Cedar Rapids",
        "state": "IA",
        "price": 187500,
        "beds": 3,
        "baths": 2,
        "sqft": 1425,
        "year_built": 1977,
        "last_sold": {
            "date": "2020-11-30",
            "price": 175000
        },
        "distance_miles": 0.2,
        "zestimate": 191000
    }
]
""")
    return str(artifact)

def get_email_template():
    artifact = Artifact(
        identifier="98acb34d", 
        type="text/plain", 
        title="Prospective Buyer Listing Email Template", 
        content="""
Dear {buyer_name},

I wanted to bring to your attention an exciting new listing at {address}, {city}, {state} that I believe would be perfect for you.

This beautiful {beds} bedroom, {baths} bathroom home offers {sqft} square feet of living space and was built in {year_built}. It is currently listed at ${price:,}, which represents excellent value for this desirable neighborhood.

Some key features that make this property stand out:
- Spacious layout with {beds} bedrooms
- {sqft} square feet of living space
- Well-maintained home built in {year_built}
- Current Zestimate: ${zestimate:,}

To give you some context about the local market, there are several comparable properties in the immediate vicinity:
- A similar {beds} bed/{baths} bath home just {distance_miles} miles away recently sold for ${last_sold[price]:,}
- Nearby properties range from ${price:,} to ${price:,} in this area
- Most homes in this neighborhood were built in the 1970s-1980s

Would you like to schedule a viewing of this property? I have several time slots available this week and would be happy to show you around.

Best regards,
Your Real Estate Agent
""")
    return str(artifact)

get_listing_schema = {
    "name": "get_listing",
    "description": "Get details about a specific property listing",
    "input_schema": {
        "type": "object",
        "properties": {
            "address": {
                "type": "string",
                "description": "The street address to look up"
            }
        },
        "required": ["address"]
    }
}

get_comparables_schema = {
    "name": "get_comparables",
    "description": "Get comparable property listings in the area",
    "input_schema": {
        "type": "object",
        "properties": {
            "address": {
                "type": "string",
                "description": "The street address to find comparables for"
            },
        },
        "required": ["address"]
    }
}

# TODO - fill in the comp blanks
get_email_template_schema = {
    "name": "get_email_template",
    "description": "Get an email template for sending property listings to prospective buyers. This is just the template, not the actual email. This template should not be edited unless the user explicitly asks to edit it. The contents of the actual instantiated email, however, can be edited.",
    "input_schema": {
        "type": "object",
        "properties": {},
    }
}


tools = [
    Tool(tool_schema=get_listing_schema, callable=get_listing),
    # Tool(tool_schema=get_comparables_schema, callable=get_comparables),
    Tool(tool_schema=get_email_template_schema, callable=get_email_template),
]