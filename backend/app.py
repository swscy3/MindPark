from app import create_app

app = create_app()

@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f"404 오류: {request.path}")
    return {'error': '요청한 리소스를 찾을 수 없습니다.'}, 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"500 서버 오류: {str(e)}")
    return {'error': '서버 내부 오류가 발생했습니다.'}, 500

if __name__ == '__main__':
    app.run(debug=True)