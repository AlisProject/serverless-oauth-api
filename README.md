# Serverless OAuth API

OAuth API for ALIS with backed Authlete.

## Initial Setup
### Install this project
```bash
# Install this project
$ git@github.com:AlisProject/serverless-oauth-api.git
$ cd serverless-oauth-api
$ npm install

# Setup libraries
$ python -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
```

### Edit enviroment variables
```bash
# Create .envrc to suit your environment.
$ cp -pr .envrc.sample .envrc
$ vi .envrc # edit

# allow
$ direnv allow
```

### Setup SSM Params
Set up `AutlteleApiKey` and `AutlteleApiSecret` ssm values with the following PR
https://github.com/AlisProject/environment/pull/24/files

ローカルでインテグレーションテストを実施してうまく動けばセットアップは完了です

## How to development
Serverless Frameworkを使用しています。基本的な使い方は以下を参照してください
https://serverless.com/framework/docs/providers/aws/

| コマンド | 用途 |
----|----
| npx serverless deploy | AWS環境へのデプロイ |
| npx serverless deploy -f <function名> | 関数単位でのデプロイ |
| npx serverless logs -f <function名> | CloudWatchLogsのログ確認 |
| npx serverless invoke local -f <function名> | 関数のローカルでの実行 |
| npx serverless invoke -f <function名> | デプロイ済みの関数の実行 |

** ステージ名とリージョンはそれぞれserverless.ymlで指定しているため、コマンドラインからの指定は不要です

### ソースコードの構成
```
|- .circleci　　　        CircleCIの設定ファイルを格納
|- lambdas  　　       　 Lambdaのハンドラー関数格納。Lambdaが発火するイベントごとにディレクトリを分ける
|- lib　　　　　　         共通で使うライブラリを格納
|- tests　　　　　　       テストコードを格納、ユニットテストとインテグレーションテストをディレクトリを分けて格納
|- serverless.yml        API及びLambdaの構成管理
|- requirements-prod.txt AWS環境にデプロイするパッケージ(テストのみで使用するパッケージは追加しない)
|- requirements.txt      テストのみで使用するものを含む全パッケージ
```

## Test
ユニットテストとインテグレーションテストを実装してください。基本的にはインテグレーションテストで正常系をテスト、
インテグレーションテストでは行えないような異常系のテストなどはユニットテストで行ってください

### ユニットテスト

以下のコマンドで実行されます。新たなエンドポイントに対するテストを追加する場合は、tests/unit配下にtest_xxxxx.pyにてファイルを追加してください
```bash
$ pytest tests/unit/ -s
```

### インテグレーションテストテスト
以下のコマンドで実行されます。新たなエンドポイントに対するテストを追加する場合は、tests/integration配下にtest_xxxxx.pyにてファイルを追加してください
```bash
$ pytest tests/integration/ --stage $INTEGRATION_TEST_STAGE --region $AWS_DEFAULT_REGION -s
```

## CI/CD
PR送信時にCIが走ります。テストを通した状態でレビュー依頼を実施してください
CDに関しては別途検討
