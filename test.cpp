#include <bits/stdc++.h>
using namespace std;

// 최대 노드 수: (단어 수 * 길이) 에 여유 조금
// 예) 510,000 단어 * 길이 10 → 5,100,000 노드 정도라 가정하고 여유 추가
const int MAX_NODE = 6000000;

struct Node {
    int child[26];
    int cnt;    // 이 노드를 루트로 하는 문자열 개수
    bool end;
    Node() {
        memset(child, 0, sizeof(child));
        cnt = 0;
        end = false;
    }
};

struct Trie {
    vector<Node> pool;
    int root;   // root 인덱스 (pool 내 인덱스)

    Trie() {
        pool.reserve(MAX_NODE); // 미리 크게 잡아서 재할당 안 나도록
        init();
    }

    // 트라이 전체 초기화 (테스트케이스마다 호출 가능)
    void init() {
        pool.clear();
        pool.push_back(Node());   // root = 0
        root = 0;
    }

    // 새 노드 생성: pool 뒤에 하나 더 붙이고 그 인덱스를 반환
    int newNode() {
        pool.push_back(Node());
        return (int)pool.size() - 1;
    }

    // 항상 존재하지 않는 새로운 단어만 insert된다고 가정
    void insert(const string& s) {
        int cur = root;
        pool[cur].cnt++;
        for (char c : s) {
            int idx = c - 'a';
            int &nxt = pool[cur].child[idx];
            if (!nxt) {
                nxt = newNode();
            }
            cur = nxt;
            pool[cur].cnt++;
        }
        pool[cur].end = true;
    }

    // 지우는 단어는 반드시 존재한다고 가정
    void erase(const string& s) {
        int cur = root;
        pool[cur].cnt--;
        for (char c : s) {
            int idx = c - 'a';
            cur = pool[cur].child[idx];   // 존재 보장
            pool[cur].cnt--;
        }
        pool[cur].end = false;
    }

    // 단어의 사전순 순위(1-based), 존재가 보장됨
    // 접두어(prefix) 단어까지 포함해서 순위 계산
    int getRank(const string& s) {
        int cur = root;
        int rank = 0;   // 나보다 앞에 있는 단어 수

        for (char c : s) {
            int idx = c - 'a';

            // 1) 지금까지의 prefix 자체가 단어면 → 항상 s보다 앞에 옴
            if (pool[cur].end) rank++;

            // 2) 현재 문자보다 앞에 있는 자식들의 subtree 개수를 모두 더함
            for (int i = 0; i < idx; i++) {
                int childIdx = pool[cur].child[i];
                if (childIdx) rank += pool[childIdx].cnt;
            }

            // 3) 현재 문자로 내려감 (존재 보장)
            cur = pool[cur].child[idx];
        }

        // 마지막으로 자기 자신(s)까지 포함
        rank++;
        return rank;
    }

    // 사전순으로 k번째 단어 (k valid 보장)
    string getKth(int k) {
        string res;
        int cur = root;

        while (true) {
            // 1) 현재 노드가 단어 끝이면, 이 단어부터 센다
            if (pool[cur].end) {
                if (k == 1) return res;  // 바로 이 단어가 k번째
                k--;                     // 이 단어 하나 건너뜀
            }

            // 2) 자식들을 'a' ~ 'z' 순으로 보면서 subtree 크기만큼 건너뛰거나 내려감
            for (int i = 0; i < 26; i++) {
                int nxt = pool[cur].child[i];
                if (!nxt) continue;
                if (pool[nxt].cnt < k) {
                    k -= pool[nxt].cnt;  // 이 subtree 전체 건너뜀
                } else {
                    // k번째 단어는 이 subtree 안에 있음 → 한 글자 추가하고 그쪽으로 이동
                    res.push_back('a' + i);
                    cur = nxt;
                    break;
                }
            }
        }
    }
};
