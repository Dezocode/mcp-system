#!/usr/bin/env python3
"""
Claude Code Integration Loop with Complete Oversight
Step-by-step prompting and workflow oversight system
"""

import sys
from pathlib import Path

import click
from claude_code_integration_loop import ClaudeCodeIntegrationLoop


def display_workflow_overview():
    """Display complete workflow overview with step definitions"""
    print("🎯 CLAUDE CODE INTEGRATION LOOP - OVERSIGHT MODE")
    print("=" * 70)
    print("📋 COMPLETE WORKFLOW OVERVIEW:")
    print()

    print("🔄 CONTINUOUS PROCESSING PHASE:")
    print("   CYCLE 1-N: Until ALL issues = 0")
    print("     ├─ STEP 1: 📊 Lint Report Generation")
    print("     │          ├─ Analyze ALL files for quality issues")
    print("     │          ├─ Generate priority fixes list")
    print("     │          └─ Count total issues found")
    print("     │")
    print("     ├─ STEP 2: 🔍 Issue Analysis & Decision")
    print("     │          ├─ Review issue count and types")
    print("     │          ├─ Confirm processing approach")
    print("     │          └─ Proceed if issues > 0")
    print("     │")
    print("     ├─ STEP 3: 🔧 Quality Patcher Execution")
    print("     │          ├─ Execute with differential restoration")
    print("     │          ├─ Apply line-level validation")
    print("     │          ├─ Use surgical code preservation")
    print("     │          └─ Process ALL available issues")
    print("     │")
    print("     └─ STEP 4: 📈 Post-Processing Analysis")
    print("                ├─ Generate post-fix lint report")
    print("                ├─ Calculate fixes applied")
    print("                ├─ Assess remaining issues")
    print("                └─ Determine if next cycle needed")
    print()

    print("🚀 DEVELOPMENT PIPELINE PHASE:")
    print("   Triggered when ALL issues = 0")
    print("     ├─ STEP 1: 📱 Development Branch Management")
    print("     │          ├─ Create/switch to development branch")
    print("     │          ├─ Merge latest main changes")
    print("     │          └─ Prepare for changes")
    print("     │")
    print("     ├─ STEP 2: 💾 Staging & Commit Changes")
    print("     │          ├─ Stage ALL processed changes")
    print("     │          ├─ Generate comprehensive commit message")
    print("     │          └─ Create commit with statistics")
    print("     │")
    print("     ├─ STEP 3: 🧪 Final Validation Tests")
    print("     │          ├─ Run comprehensive lint validation")
    print("     │          ├─ Execute Python syntax checks")
    print("     │          └─ Ensure 0 issues before publishing")
    print("     │")
    print("     ├─ STEP 4: 🔖 Version Bump & Tagging")
    print("     │          ├─ Bump version using version keeper")
    print("     │          ├─ Create development tag")
    print("     │          └─ Prepare for release")
    print("     │")
    print("     ├─ STEP 5: ⬆️ Remote Publishing")
    print("     │          ├─ Push development branch to remote")
    print("     │          ├─ Push all tags")
    print("     │          └─ Ensure branch is published")
    print("     │")
    print("     └─ STEP 6: 📋 Release Documentation")
    print("                ├─ Generate development release docs")
    print("                ├─ Create pipeline completion report")
    print("                └─ Provide next steps guidance")
    print()

    print("✅ FINAL OUTCOME:")
    print("   • ALL 875+ issues resolved and applied")
    print("   • Development branch published to remote")
    print("   • Comprehensive documentation generated")
    print("   • System ready for testing and integration")
    print()


@click.command()
@click.option(
    "--max-cycles",
    default=999,
    help="Maximum processing cycles",
)
@click.option(
    "--target-issues",
    default=0,
    help="Target remaining issues (0 = all resolved)",
)
@click.option(
    "--enable-pipeline",
    is_flag=True,
    default=True,
    help="Enable development branch publishing",
)
@click.option(
    "--non-interactive",
    is_flag=True,
    help="Run without confirmation prompts (for orchestrator)",
)
def main(
    max_cycles,
    target_issues,
    enable_pipeline,
    non_interactive,
):
    """
    Claude Code Integration Loop with Complete Step-by-Step Oversight

    This mode provides comprehensive workflow oversight with:
    • Step-by-step prompting for each action
    • Clear explanations of what each step will do
    • User confirmation before proceeding
    • Detailed progress reporting and analysis
    • Complete transparency in the process
    """

    # Display workflow overview
    display_workflow_overview()

    print("🔥 EXECUTION PARAMETERS:")
    print(f"   • Max Cycles: {max_cycles}")
    print(f"   • Target Issues: {target_issues}")
    print(f"   • Pipeline Publishing: {'ENABLED' if enable_pipeline else 'DISABLED'}")
    print("   • Mode: Step-by-step with oversight prompting")
    print()

    print("⚠️  IMPORTANT NOTICES:")
    print("   • Each step will prompt for confirmation")
    print("   • Process can be interrupted at any prompt")
    print("   • All actions will be clearly explained before execution")
    print("   • Progress will be tracked and reported in detail")
    print()

    # Final confirmation to begin (skip in non-interactive mode)
    if non_interactive:
        print("🤖 NON-INTERACTIVE MODE: Auto-starting execution...")
        response = "yes"
    else:
        response = input(
            "🎯 Ready to begin full scale execution with oversight? (yes/no): "
        ).lower()
        if response != "yes":
            print("❌ Execution cancelled by user")
            sys.exit(0)

    # Initialize and configure loop system
    loop_system = ClaudeCodeIntegrationLoop(
        repo_path=Path.cwd(),
        non_interactive=non_interactive,
    )
    loop_system._publish_pipeline = enable_pipeline

    try:
        # Execute with oversight
        print("\n🚀 STARTING OVERSIGHT-ENABLED EXECUTION")
        print("=" * 70)

        if non_interactive:
            print("\n" + "=" * 80)
            print("🤖 CLAUDE CLI INTEGRATION MODE ACTIVATED")
            print("=" * 80)
            print("📋 CLAUDE: You are now integrated with the oversight workflow!")
            print("💡 INSTRUCTIONS:")
            print("   • The workflow will show you exactly what needs to be done")
            print("   • When the quality patcher runs, it will ask you to apply fixes")
            print("   • Use your Write/Edit tools to apply each fix as shown")
            print("   • The system will validate your changes automatically")
            print("   • Continue until all issues are resolved")
            print("=" * 80)
            print("🚀 Starting automated workflow execution...")
            print("=" * 80 + "\n")

        results = loop_system.run_continuous_rerun_until_resolved(
            max_cycles=max_cycles,
            target_issues_remaining=target_issues,
        )

        # Final results analysis
        print("\n🏆 EXECUTION COMPLETE - FINAL ANALYSIS")
        print("=" * 70)

        target_achieved = results.get("target_achieved", False)
        pipeline_executed = results.get("pipeline_execution", {})
        pipeline_success = pipeline_executed.get("overall_success", False)
        branch_published = pipeline_executed.get(
            "development_branch_published",
            False,
        )

        if target_achieved:
            print("✅ PRIMARY OBJECTIVE: ALL ISSUES RESOLVED")

            if enable_pipeline:
                if pipeline_success and branch_published:
                    print("✅ PIPELINE OBJECTIVE: DEVELOPMENT BRANCH PUBLISHED")
                    print(
                        "🎉 COMPLETE SUCCESS! System ready for testing and integration"
                    )
                else:
                    print("❌ PIPELINE OBJECTIVE: Publishing failed")
                    print(
                        "⚠️  Issues resolved but branch not published - "
                        "check pipeline report"
                    )
            else:
                print("ℹ️  Pipeline publishing was disabled - issues resolved only")
        else:
            final_issues = results.get(
                "final_issues_remaining",
                "Unknown",
            )
            print(f"❌ PRIMARY OBJECTIVE: {final_issues} issues still remain")
            print("⚠️  Target not achieved - review cycle reports for details")

        print("\n📋 Comprehensive reports generated in .claude_loops/")
        print("🔍 Check pipeline completion report for detailed next steps")

        # Exit with appropriate code
        if target_achieved and (
            not enable_pipeline or (pipeline_success and branch_published)
        ):
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 EXECUTION INTERRUPTED BY USER")
        print("ℹ️  Process can be resumed by running the command again")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ EXECUTION ERROR: {e}")
        print("🔍 Check logs and reports for detailed error information")
        sys.exit(2)


if __name__ == "__main__":
    main()
