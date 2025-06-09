$testDir = "pass"
$script = "myrpal.py"
$testFiles = Get-ChildItem $testDir

Write-Host "Select an option:"
Write-Host "1 - Run normal tests"
Write-Host "2 - Run tests with -ast"
$choice = Read-Host "Enter your choice (1 or 2)"

switch ($choice) {
    "1" {
        foreach ($file in $testFiles) {
            Write-Host "`nRunning normal test for $($file.Name)"
            Write-Host "Answer: "
            python $script $file.FullName
            Write-Host "`n "
        }
    }
    "2" {
        foreach ($file in $testFiles) {
            Write-Host "`nRunning AST test for $($file.Name)"
            Write-Host "Answer: "
            python $script -ast $file.FullName
            Write-Host "`n "
        }
    }
    default {
        Write-Host "Invalid choice. Please enter 1 or 2."
    }
}
