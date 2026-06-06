# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Overview
The objective of this project is to build a facts-only FAQ assistant for mutual fund schemes, using Groww as the reference product context. The assistant will answer objective, verifiable queries related to mutual funds by retrieving information exclusively from official public sources, such as AMC (Asset Management Company) websites, AMFI, and SEBI.

The system must strictly avoid providing investment advice, opinions, or recommendations. Every response must include a single, clear source link and adhere to defined constraints around clarity, accuracy, and compliance.

## Objective
Design and implement a lightweight Retrieval-Augmented Generation (RAG)-based assistant that:
- Answers factual queries about mutual fund schemes.
- Uses a curated corpus of official documents.
- Provides concise, source-backed responses.

## Target Users
- **Retail investors** comparing mutual fund schemes.
- **Customer support and content teams** handling repetitive mutual fund queries.

## Scope of Work

### 1. Corpus Definition
The project is limiting its corpus to the following 5 mutual fund scheme URLs from Groww:
1. [HDFC Silver ETF FoF (Direct Growth)](https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth)
2. [HDFC Small Cap Fund (Direct Growth)](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)
3. [HDFC Defence Fund (Direct Growth)](https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth)
4. [HDFC Gold ETF Fund of Fund (Direct Plan Growth)](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth)
5. [HDFC Mid-Cap Opportunities Fund (Direct Growth)](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)

The assistant retrieves information from the official details provided in these URLs and their underlying official sources.

### 2. FAQ Assistant Requirements
The assistant must answer facts-only queries, including:
- **Scheme Details**: Expense ratio, exit load details, minimum SIP amount, ELSS lock-in period, riskometer classification, benchmark index.
- **Fund Management Data**: Details about the fund managers, their credentials, experience, and the funds they manage.
- **Operational Processes**: Process to download statements or capital gains reports.

**Response Formatting Constraints:**
- Each response must be limited to a **maximum of 3 sentences**.
- Each response must include **exactly one citation link**.
- Each response must include a footer: `Last updated from sources: <date>`.

### 3. Refusal Handling
The assistant must refuse non-factual, speculative, or advisory queries, such as:
- *"Should I invest in this fund?"*
- *"Which fund is better?"*

**Refusal Response Requirements:**
- Be polite and clearly worded.
- Reinforce the facts-only limitation.
- Provide a relevant educational link (e.g., AMFI or SEBI resource).

### 4. User Interface (Minimal)
The solution should include a simple interface featuring:
- A welcome message.
- Three example questions.
- A visible disclaimer: `Facts-only. No investment advice.`

## Constraints

### Data and Sources
- Use only official public sources (AMC, AMFI, SEBI, and official Groww fund detail pages).
- Do not use third-party blogs or aggregator websites.

### Privacy and Security
- Do not collect, store, or process sensitive personal data, including:
  - PAN or Aadhaar numbers
  - Account numbers
  - OTPs
  - Email addresses or phone numbers

### Content Restrictions
- **No investment advice or recommendations.**
- **No performance comparisons or return calculations.**
- For performance-related queries, provide a link to the official factsheet only.

### Transparency
- Responses must be short, factual, and verifiable.
- Every answer must include a source link and the last updated date.

## Expected Deliverables
- **README Document**: Setup instructions, selected AMC and schemes, architecture overview (RAG approach), and known limitations.
- **Disclaimer Snippet**: `Facts-only. No investment advice.`

## Success Criteria
- Accurate retrieval of factual mutual fund information.
- Strict adherence to facts-only responses.
- Consistent inclusion of valid source citations.
- Proper refusal of advisory queries.
- Clean, minimal, and user-friendly interface.

## Summary
The goal is to build a trustworthy, transparent, and compliant mutual fund FAQ assistant that prioritizes accuracy over intelligence. The system should ensure that users receive only verified, source-backed financial information, without any advisory bias or speculative content.
