"""
DynamoDB 설정 및 초기화 스크립트
"""

import streamlit as st
from dynamodb_schema import DynamoDBSchema
from migrate_to_dynamodb import DataMigrator
from aws_config import aws_config

def main():
    st.title("🤖 DynamoDB 설정 및 마이그레이션")
    
    st.markdown("""
    이 페이지는 SQLite에서 DynamoDB로 마이그레이션하는 과정을 도와줍니다.
    """)
    
    # 단계별 진행
    step = st.selectbox(
        "진행할 단계를 선택하세요:",
        [
            "1. AWS 연결 테스트",
            "2. DynamoDB 테이블 생성",
            "3. 샘플 데이터 생성",
            "4. SQLite 데이터 마이그레이션",
            "5. 완료 확인"
        ]
    )
    
    if step == "1. AWS 연결 테스트":
        st.subheader("AWS 연결 테스트")
        
        with st.form("aws_test_form"):
            access_key = st.text_input("AWS Access Key ID", type="password")
            secret_key = st.text_input("AWS Secret Access Key", type="password")
            region = st.selectbox("AWS Region", ["ap-northeast-2", "us-east-1", "us-west-2"], index=0)
            
            if st.form_submit_button("연결 테스트"):
                if access_key and secret_key:
                    try:
                        aws_config.setup_credentials(access_key, secret_key, region)
                        if aws_config.test_connection():
                            st.success("✅ AWS 연결 성공!")
                            st.session_state.aws_configured = True
                        else:
                            st.error("❌ AWS 연결 실패")
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {e}")
                else:
                    st.warning("모든 필드를 입력해주세요.")
    
    elif step == "2. DynamoDB 테이블 생성":
        st.subheader("DynamoDB 테이블 생성")
        
        if st.button("테이블 생성"):
            try:
                schema = DynamoDBSchema()
                table = schema.create_table()
                st.success("✅ 테이블이 성공적으로 생성되었습니다!")
                st.json({
                    "테이블 이름": table.table_name,
                    "상태": "활성"
                })
            except Exception as e:
                st.error(f"❌ 테이블 생성 실패: {e}")
    
    elif step == "3. 샘플 데이터 생성":
        st.subheader("샘플 데이터 생성")
        
        if st.button("샘플 데이터 생성"):
            try:
                schema = DynamoDBSchema()
                schema.create_sample_data()
                st.success("✅ 샘플 데이터가 성공적으로 생성되었습니다!")
            except Exception as e:
                st.error(f"❌ 샘플 데이터 생성 실패: {e}")
    
    elif step == "4. SQLite 데이터 마이그레이션":
        st.subheader("SQLite 데이터 마이그레이션")
        
        st.info("기존 SQLite 데이터베이스의 모든 데이터를 DynamoDB로 마이그레이션합니다.")
        
        if st.button("마이그레이션 시작"):
            try:
                migrator = DataMigrator()
                success = migrator.migrate_all_data()
                
                if success:
                    st.success("✅ 데이터 마이그레이션이 완료되었습니다!")
                else:
                    st.error("❌ 데이터 마이그레이션에 실패했습니다.")
            except Exception as e:
                st.error(f"❌ 마이그레이션 중 오류 발생: {e}")
    
    elif step == "5. 완료 확인":
        st.subheader("완료 확인")
        
        try:
            from dynamodb_manager import dynamodb_manager
            
            # 사용자 수 확인
            users = dynamodb_manager.get_users()
            st.metric("사용자 수", len(users))
            
            # 로봇 수 확인
            robots = dynamodb_manager.get_robots()
            st.metric("로봇 수", len(robots))
            
            # 프로젝트 수 확인
            projects = dynamodb_manager.get_projects()
            st.metric("프로젝트 수", len(projects))
            
            # 통계 데이터 확인
            stats = dynamodb_manager.get_dashboard_stats()
            st.subheader("대시보드 통계")
            st.json(stats)
            
            st.success("✅ DynamoDB 설정이 완료되었습니다!")
            st.info("이제 `main_dynamodb.py`를 실행하여 DynamoDB 버전의 애플리케이션을 사용할 수 있습니다.")
            
        except Exception as e:
            st.error(f"❌ 확인 중 오류 발생: {e}")
    
    # 사이드바에 도움말
    with st.sidebar:
        st.markdown("## 📋 설정 체크리스트")
        st.markdown("""
        - [ ] AWS 계정 생성
        - [ ] IAM 사용자 생성
        - [ ] AWS 자격 증명 설정
        - [ ] DynamoDB 테이블 생성
        - [ ] 데이터 마이그레이션
        - [ ] 애플리케이션 테스트
        """)
        
        st.markdown("## 🔗 유용한 링크")
        st.markdown("""
        - [AWS 콘솔](https://console.aws.amazon.com/)
        - [DynamoDB 문서](https://docs.aws.amazon.com/dynamodb/)
        - [boto3 문서](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
        """)

if __name__ == "__main__":
    main()
