[![CircleCI](https://circleci.com/gh/AlisProject/serverless-oauth-api/tree/master.svg?style=svg&circle-token=e71816ed083a9ca2eb20f56c6ede43d56f2e4af4)](https://circleci.com/gh/AlisProject/serverless-oauth-api/tree/master)

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
Set up `AutlteleApiKey` and `AutlteleApiSecret` ssm values with the following link.
https://github.com/AlisProject/environment

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

## CI
PR送信時にCIが走ります。テストを通した状態でレビュー依頼を実施してください

## デプロイ
本GitHub上でtagを作るとデプロイパッケージがS3バケットにputされます。環境変数DEPLOYMENT_BUCKETにデプロイしたいバケット名を指定してください。
指定したtagをS3オブジェクトのprefixとしてデプロイパッケージがアップロードされます。

```bash
$ git tag 1.0.0
$ git push origin 1.0.0
```

上記のデプロイが正常終了後は以下のaws-cliでCloudFormationテンプレートを反映させてください。なお、stack-nameは自由に決めて構いません。

新規追加時

```bash
$ aws cloudformation create-stack --stack-name <スタック名> --template-url https://s3-ap-northeast-1.amazonaws.com/<バケット名>/<tag名>/cloudformation-template-update-stack.json --capabilities '["CAPABILITY_IAM","CAPABILITY_NAMED_IAM"]'
```

既存stack更新時

```bash
$ aws cloudformation update-stack --stack-name <スタック名> --template-url https://s3-ap-northeast-1.amazonaws.com/<バケット名>/<tag名>/cloudformation-template-update-stack.json --capabilities '["CAPABILITY_IAM","CAPABILITY_NAMED_IAM"]'
```


## ドメインの割当

APIをデプロイ後にdns-templateのスタックをデプロイすることでドメインが割り当てられます

```
aws cloudformation deploy --stack-name <スタック名> --template /path/to/dns-template.yml --capabilities '["CAPABILITY_AUTO_EXPAND"]' --parameter-overrides AlisAppId=$ALIS_APP_ID Doamin=<ネイキッドドメイン> SubDomain=<サブドメイン> HostedZoneId=<Route53のゾーンID> RestApiId=<割り当てたいAPIのID> CertificateArn=<ACMで発行した証明書のARN>
```
