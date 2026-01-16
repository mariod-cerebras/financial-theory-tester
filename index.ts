#!/usr/bin/env bun
/**
 * Financial Theory Tester CLI
 * Test financial theories on stocks of your choice
 */

import { $ } from "bun"

interface TestResult {
  theory: string
  interpretation: string
  makesSense: boolean
  [key: string]: any
}

interface TheoryTestResults {
  ticker: string
  period: string
  tests: TestResult[]
  summary: {
    makesSenseCount: number
    totalTests: number
  }
}

async function runFinancialTheoryTests(ticker: string, period: string = "2y"): Promise<TheoryTestResults> {
  const scriptPath = import.meta.dir + "/financial_theory_tester.py"

  const result = (await $`python3 ${scriptPath} ${ticker} ${period}`.text()) ?? ""

  // Parse the output (simplified - in production you'd want structured JSON output)
  const tests: TestResult[] = []
  let currentTest: Partial<TestResult> | null = null

  const lines = result.split("\n")
  for (const line of lines) {
    if (line.startsWith("📊")) {
      if (currentTest) {
        tests.push(currentTest as TestResult)
      }
      currentTest = {
        theory: line.replace("📊", "").trim(),
        makesSense: false,
      }
    } else if (line.includes("Interpretation:") && currentTest) {
      const parts = line.split("Interpretation:")
      if (parts[1]) {
        currentTest.interpretation = parts[1].trim()
      }
    } else if (line.includes("Makes Sense:") && currentTest) {
      currentTest.makesSense = line.includes("✓ Yes")
    }
  }

  if (currentTest) {
    tests.push(currentTest as TestResult)
  }

  const makesSenseCount = tests.filter((t) => t.makesSense).length

  return {
    ticker,
    period,
    tests,
    summary: {
      makesSenseCount,
      totalTests: tests.length,
    },
  }
}

async function main() {
  const args = process.argv.slice(2)

  if (args.length === 0) {
    console.log("Usage: bun run index.ts <TICKER> [period]")
    console.log("Example: bun run index.ts AAPL 2y")
    console.log("Period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max")
    process.exit(1)
  }

  const ticker = args[0] ?? ""
  const period = args[1] ?? "2y"

  console.log(`Running financial theory tests for ${ticker}...`)
  console.log()

  const results = await runFinancialTheoryTests(ticker, period)

  console.log(`\n${"=".repeat(60)}`)
  console.log(`FINANCIAL THEORY TEST RESULTS: ${results.ticker}`)
  console.log(`${"=".repeat(60)}\n`)

  for (const test of results.tests) {
    console.log(`📊 ${test.theory}`)
    console.log(`   Interpretation: ${test.interpretation}`)
    console.log(`   Makes Sense: ${test.makesSense ? "✓ Yes" : "✗ No"}`)
    console.log()
  }

  console.log(`${"=".repeat(60)}`)
  console.log(
    `SUMMARY: ${results.summary.makesSenseCount}/${results.summary.totalTests} theories make sense for ${results.ticker}`,
  )
  console.log(`${"=".repeat(60)}`)
}

main()
