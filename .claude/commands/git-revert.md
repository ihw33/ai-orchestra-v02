# Git 특정 시점으로 되돌리기

특정 커밋으로 코드를 되돌립니다.

사용법: `/git-revert <commit-hash>`

```bash
git reset --hard {{COMMIT_HASH}}
```

예시:
- `/git-revert a1b2c3d` - 해당 커밋으로 되돌리기
- `/git-log`로 먼저 커밋 해시 확인 후 사용