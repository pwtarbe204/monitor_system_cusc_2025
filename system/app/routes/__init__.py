def register_routes(app):
    from .auth_routes import auth_bp
    from .dashboard_routes import dashboard_bp
    from .group_routes import group_bp
    from .api_routes import api_bp
    from .chart_routes import chart_bp
    from .report_routes import report_bp
    from .checker_routes import checker_bp
    from .speedtest_routes import speedtest_bp
    from .setting_routes import setting_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(group_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(chart_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(checker_bp)
    app.register_blueprint(speedtest_bp)
    app.register_blueprint(setting_bp)